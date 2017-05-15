# coding:utf-8


class FlowRule(object):
    """ 流表内部以及流表之间的规则，用于校验自定义内容 """
    def __str__(self):
        return self.string

    def __init__(self, string):
        self.string = string.strip()
        self.left_table_index = 0
        self.left_field = ''
        self.left_field_scope = ''

        self.right_table_index = 0
        self.right_field = ''
        self.right_field_scope = ''

        self.relationship = '=='
        self.parse_rule_str()

    def parse_rule_str(self, ):
        """ table0.tun_id == table100.tun_id  or table0.action.tun_id != 0 """

        rule_str = self.string.strip()
        index = rule_str.find('==')
        if index == -1:
            index = rule_str.find('!=')
            if index == -1:
                print('error rule str: not find \'==\' or \'!=\'!')
                return False
            else:
                self.relationship = '!='

        left_table_and_field = rule_str[:index].strip()
        right_table_and_field = rule_str[index+2:].strip()

        result1, left_table_index, left_scope, left_field = self.__class__.parse_table_field(left_table_and_field)
        result2, right_table_index, right_scope, right_field = self.__class__.parse_table_field(right_table_and_field)
        if result1 is False or result2 is False:
            return False

        if left_table_index == -1 and right_table_index == -1:
            return False

        if left_table_index == -1:
            self.left_table_index = right_table_index
            self.left_field = right_field
            self.left_field_scope = right_scope

            self.right_table_index = left_table_index
            self.right_field = left_field
            self.right_field_scope = left_scope
        else:
            self.left_table_index = left_table_index
            self.left_field = left_field
            self.left_field_scope = left_scope

            self.right_table_index = right_table_index
            self.right_field = right_field
            self.right_field_scope = right_scope

        return True

    @classmethod
    def parse_rules_str(cls, rules_str):
        """ table0.match.tun_id == table100.action.tun_id && table0.match.tun_id != 0 """
        rules = {}
        rule_strings = rules_str.split('&&')
        for rule_str in rule_strings:
            rule = FlowRule(rule_str)

            if rule.left_table_index == -1:
                key = rule.right_field
            elif rule.right_table_index == -1:
                key = rule.left_field
            elif rule.left_field == rule.right_field:
                key = rule.left_field
            else:
                print 'left_field(%s) must equal to right_field(%s)!' % (rule.left_field, rule.right_field)
                continue

            if key in rules:
                rules[key].append(rule)
            else:
                rules[key] = [rule]
        return rules

    # 返回 (True, left_table_index, field, right_table_index, field)
    @classmethod
    def parse_table_field(cls, string):
        """ table0.action.tun_id """
        if string.startswith('table') is False:
            return True, -1, 'match', int(string)

        index = string.find('.')
        if index == -1:
            print('error rule str[%s]: not find .!' % string)
            return False, 0, '', 0

        items = string.split('.')
        if len(items) != 3:
            print "rule string[%s] is invalid!" % string
            return False, 0, '', 0

        table_index = items[0][len('table'):].strip()
        field_scope = items[1].strip()
        field = items[2].strip()
        return True, int(table_index), field_scope, field
