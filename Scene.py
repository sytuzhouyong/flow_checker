# coding:utf-8

import copy
from Flow import *
from utils import *
from test import *


class Scene(object):
    def __init__(self, name):
        self.name = name
        self.flows = []
        self.rules = []
        self.jump_flow = Flow('')
        self.jumped_flows = []  # 跳转经过的流表集合

    def init_flow(self,):
        self.jump_flow.match_fields['table'] = 0

    # 验证场景流表是否配置成功
    def validate(self):
        jump_flow = self.jump_flow

        if len(self.flows) == 0:
            print "no flows found in current %s scene" % self.name
            return False, None

        for flow in self.flows:
            jump_flow = self.jump_to_next_flow(jump_flow, self.rules)
            if jump_flow is None:
                print('miss flow[%s]!' % flow.text)
                return False, None

            # check jump flow is right or not
            if self.match(jump_flow, flow, self.rules) is False:
                print('match flow failed, expected[%s],\n\t but[%s]!' % (flow.text, jump_flow.text))
                return False, None

            print('flow[%s]\n\t ------------------------match success' % jump_flow.text)
            self.jumped_flows.append(copy.deepcopy(jump_flow))
            jump_flow = jump_flow.execute()

        # 校验最终的流表是否是预期的流表
        last_flow = self.jumped_flows[-1]
        for field, value in last_flow.action_fields.items():
            if field in jump_flow.match_fields:
                actual_value = jump_flow.match_fields[field]
                expected_value = last_flow.action_fields[field]
                if actual_value == expected_value:
                    continue

                result = self.match_field_with_rules(last_flow, self.flows[-1], field, self.rules)
                if result is True:
                    continue

                print 'last flow is not matched'
                return False, None
            else:
                result = self.match_field_with_rules(last_flow, self.flows[-1], field, self.rules)
                if result is True:
                    continue

                print 'last flow is not matched'
                return False, None

        return True, last_flow

    def match_field_with_rules(self, src_flow, dst_flow, field, rules):
        # 如果匹配域在规则列表中,则执行匹配规则; 如果不在就执行字段比较
        if field not in rules:
            return False

        # 给定的field是否匹配规则
        field_rules = rules[field]
        for rule in field_rules:
            right_value = -1

            left_flow = flow_of_index(self.jumped_flows, rule.left_table_index)
            if left_flow is None:
                left_flow = dst_flow

            if rule.left_field_scope == 'match':
                left_value = left_flow.match_fields[field]
            elif rule.left_field_scope == 'action':
                left_value = left_flow.action_fields[field]

            # 只有一端有table, eg. table0.action.tun_id != 0
            if rule.right_table_index == -1:
                right_value = rule.right_field
            else:
                # right_value就是当前src_flow里面的值,因为此时由于src_flow里面的值和标准flow里面的值不一样，才会执行到这里，
                # 而此时src_flow还没有加入到jumped_flows中，只有rule通过才会加入到jumped_flows中
                right_flow = src_flow
                # table不相等，说明该规则和流表不匹配，忽略
                if right_flow.table != rule.right_table_index:
                    continue

                if rule.right_field_scope == 'match':
                    right_value = right_flow.match_fields[field]
                elif rule.left_field_scope == 'action':
                    right_value = right_flow.action_fields[field]

            if rule.relationship == '==':
                if left_value != right_value:
                    print 'rule[%s] match failed' % rule.string
                    return False
            elif rule.relationship == '!=':
                if left_value == right_value:
                    print 'rule[%s] match failed' % rule.string
                    return False
            else:
                print 'do not support relationship[%s]' % rule.relationship
                return False
        return True

    # src_flow 能否匹配 dst_flow; rules: {'field': [FlowRule]}
    def match(self, src_flow, dst_flow, rules):
        if src_flow.table != dst_flow.table:
            # print('flow match failed, expect table%d but table%d' % (dst_flow.table, src_flow.table))
            return False

        # 查看match域是否能匹配
        for field, value in dst_flow.match_fields.items():
            # 弱匹配项
            if field in ['cookie', 'duration', 'n_packets', 'n_bytes', 'hard_age', 'idle_age', 'priority']:
                continue

            # dst_flow中的匹配域在src_flow中没有
            if field not in src_flow.match_fields:
                if self.match_field_with_rules(src_flow, dst_flow, field, rules) is not True:
                    print('flow[%s]\n\t match failed, table%s: %s = %s missed!'
                          % (dst_flow.text, src_flow.match_fields['table'], field, value))
                    return False
                continue

            actual_value = src_flow.match_fields[field]
            if value == actual_value:
                continue

            if self.match_field_with_rules(src_flow, dst_flow, field, rules) is not True:
                print('flow[%s]\n\t match failed, expect: %s = %s, but is %s'
                      % (dst_flow.text, field, value, actual_value))
                return False

        return True

    def jump_to_next_flow(self, src_flow, rules):
        if is_test == 1:
            flows_str = test_flows[str(src_flow.table)]
        else:
            cmd_str = 'ovs-ofctl dump-flows br-int table=%d' % src_flow.table
            # print('execute cmd: %s' % cmd_str)
            flows_str = execute_command(cmd_str)

        flow_strings = flows_str.split('\n')
        del flow_strings[0]

        matched_flow = None
        for flow_string in flow_strings:
            # print(string)
            flow_string = flow_string.strip()
            if len(flow_string) == 0:
                continue

            item = Flow(flow_string)
            if self.match(src_flow, item, rules) is True:
                if matched_flow is None or item.priority > matched_flow.priority:
                    # print('flow[%s]\n\t ---------match success' % item.text)
                    matched_flow = item
                else:
                    print "flow[%s]\n\t match failed, priority is smaller than flow[%s]." \
                          % (item.text, matched_flow.text)

        if matched_flow is not None:
            # 将当前的flow的匹配域集成到匹配的flow中
            matched_flow.match_fields.update(src_flow.match_fields)
            matched_flow.priority = src_flow.priority

        return matched_flow
