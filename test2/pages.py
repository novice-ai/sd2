#-*- coding: utf-8 -*-
from __future__ import division

from otree.api import *
import random
import math
from ._builtin import Page, WaitPage
from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range
)

class C(BaseConstants):
    NAME_IN_URL = 'test'
    # number of players in a group - should be a multiple of 2 (6)
    PLAYERS_PER_GROUP = 2
    # the number of rounds to play - should be a multiple of 4
    NUM_ROUNDS = 40
    LOW_COST_OF_TRAINING = 200
    HIGH_COST_OF_TRAINING = 600
    SIGNALING_COST = 100
    WORKER_HIRE_INVEST = 1800
    WORKER_HIRE_NOT_INVEST = 1400
    WORKER_NOT_HIRE_INVEST = 1000
    WORKER_NOT_HIRE_NOT_INVEST = 1200
    FIRM_HIRE_INVEST = 1600
    FIRM_HIRE_NOT_INVEST = 400
    FIRM_NOT_HIRE_INVEST = 1200
    FIRM_NOT_HIRE_NOT_INVEST = 1200
    BIG_PRIZE = 200
    SMALL_PRIZE = 0
    COLORS = ["PURPLE", "GREEN"]
    
class Computer_Number(Page):
    form_model = 'player'  
    form_fields = ['computer_num']
    def is_displayed(self):
        second_stage_start = self.subsession.num_first_stage_rounds
        return self.round_number == 1

class Begin_Experiment(Page):
    form_model = '' 
    form_fields = []
    def is_displayed(self):
        second_stage_start = self.subsession.num_first_stage_rounds
        # third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        # fourth_stage_start = (
        #     self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        return self.round_number == 1

    def vars_for_template(self):

        instructions_text = "請等實驗者告知「實驗正式開始」，再按「下一頁」，謝謝!"

        return {
            'instructions_text': instructions_text,
        }
    
class Reveal_Signal(Page):
    form_model = 'group'
    def get_form_fields(self):
        # Use self.session.config to conditionally set form fields
        if self.subsession.treatment == 11:
            return ['reveal_type', 'send_signal']
        elif self.subsession.treatment == 1:
            return ['send_signal']
        elif self.subsession.treatment == 10:
            return ['reveal_type']
        else:
            return []

    def vars_for_template(self):
        green_invest_count = 0.
        purple_invest_count = 0.
        green_hiring_count = 0.
        purple_hiring_count = 0.
        green_count = 0
        purple_count = 0
        for s in self.subsession.in_previous_rounds():        
            for g in s.get_groups():            
                if g.worker_color == 'GREEN':
                    green_count += 1
                    if g.worker_invest:
                        green_invest_count += 1                    
                    if g.firm_hire:
                        green_hiring_count += 1                      
                elif g.worker_color == 'PURPLE':
                    purple_count += 1
                    if g.worker_invest:
                        purple_invest_count += 1                       
                    if g.firm_hire:
                        purple_hiring_count += 1                        
        if green_count == 0:
            self.group.green_invest_rate_shown = '0.0'
            self.group.green_hire_rate_shown = '0.0'
        else:
            self.group.green_invest_rate_shown = str(round(green_invest_count / green_count, 2))
            self.group.green_hire_rate_shown = str(round(green_hiring_count / green_count, 2))

        if purple_count == 0:
            self.group.purple_invest_rate_shown = '0.0'
            self.group.purple_hire_rate_shown = '0.0'
        else:
            self.group.purple_invest_rate_shown = str(round(purple_invest_count / purple_count, 2))
            self.group.purple_hire_rate_shown = str(round(purple_hiring_count / purple_count, 2))

        if purple_count + green_count == 0:
            self.group.avg_hire_rate_shown = '0.0'
            self.group.avg_invest_rate_shown = '0.0'
        else:
            self.group.avg_hire_rate_shown = str(round((purple_hiring_count + green_hiring_count)/(green_count+purple_count) , 2))
            self.group.avg_invest_rate_shown = str(round((purple_invest_count + green_invest_count)/(green_count+purple_count) , 2))           

        table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
        table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
        table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
        table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
        second_stage_start = self.subsession.num_first_stage_rounds
        # third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        # fourth_stage_start = (
        #     self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        # if third_stage_start < self.subsession.round_number <= fourth_stage_start and self.group.worker_color == 'PURPLE':
        #     table_invest_hire = "{0} - c, {1} + s".format(str(C.WORKER_HIRE_INVEST),
        #                                                   str(C.FIRM_HIRE_INVEST))
        #     table_not_invest_hire = "{0}, {1} + s".format(str(C.WORKER_HIRE_NOT_INVEST),
        #                                                   str(C.FIRM_HIRE_NOT_INVEST))

        green_cost = 0
        purple_cost = 0
        extra_text_green = ""
        extra_text_purple = ""
        extra_text_type = ""
        instructions_text = ""
        instructions_text_2 = ""
        instructions_text_3 = ""

        stage_num = 0
        if 0 < self.round_number <= second_stage_start/2:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.HIGH_COST_OF_TRAINING
            stage_num = 1
            stage_round = self.round_number
            extra_text_type = "您配對到 " + str(self.group.worker_color) + " 的求職者。"
        elif second_stage_start/2 < self.round_number <= second_stage_start:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.LOW_COST_OF_TRAINING
            stage_num = 1
            stage_round = self.round_number
            extra_text_type = "您配對到 " + str(self.group.worker_color) + " 的求職者。"
        elif second_stage_start < self.round_number:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.LOW_COST_OF_TRAINING
            stage_num = 2
            stage_round = self.round_number - second_stage_start
        return {
            'table_invest_hire': str(table_invest_hire),
            'table_invest_not_hire': str(table_invest_not_hire),
            'table_not_invest_hire': str(table_not_invest_hire),
            'table_not_invest_not_hire': str(table_not_invest_not_hire),
            'green_invest_rate': self.group.green_invest_rate_shown,
            'purple_invest_rate': self.group.purple_invest_rate_shown,
            'green_hiring_rate': self.group.green_hire_rate_shown,
            'purple_hiring_rate': self.group.purple_hire_rate_shown,
            'green_invest_count': str(green_invest_count),
            'purple_invest_count': str(purple_invest_count),
            'green_hiring_count': str(green_hiring_count),
            'purple_hiring_count': str(purple_hiring_count),
            'avg_hiring_rate': self.group.avg_hire_rate_shown,
            'avg_invest_rate': self.group.avg_invest_rate_shown,
            'worker_color': str(self.group.worker_color),
            'cost_of_training': str(self.group.cost_of_training),
            'graph_purple_invest_rate': safe_json(self.group.purple_invest_rate_shown),
            'graph_green_invest_rate': safe_json(self.group.green_invest_rate_shown),
            'graph_purple_hiring_rate': safe_json(self.group.purple_hire_rate_shown),
            'graph_green_hiring_rate': safe_json(self.group.green_hire_rate_shown),
            'purple_cost': str(purple_cost),
            'green_cost': str(green_cost),
            'extra_text_green': str(extra_text_green),
            'extra_text_purple': str(extra_text_purple),
            'extra_text_type': str(extra_text_type),
            'stage_num': str(stage_num),
            'stage_round': str(stage_round)
        }
    def is_displayed(self):
        # third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        return self.player.id_in_group == 1 and self.round_number > self.subsession.num_first_stage_rounds and self.subsession.treatment != 0 and self.subsession.treatment != -1

class WaitForWorkers(WaitPage):
    wait_for_all_groups = False
    
    title_text = ""
    body_text = "請稍待求職者做決策，謝謝！" 
    def is_displayed(self):
        # third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        return self.player.id_in_group == 2 and self.round_number > self.subsession.num_first_stage_rounds and self.subsession.treatment != 0           
        
class Worker(Page):
    form_model = 'group'

    def is_displayed(self):
        return self.player.id_in_group == 1 and self.round_number <= self.subsession.num_rounds

    def get_form_fields(self):
        if self.subsession.use_worker_belief_elicitation:
            return ['worker_invest', 'worker_hiring_belief']
        else:
            return ['worker_invest']

    def vars_for_template(self):

        green_invest_count = 0.
        purple_invest_count = 0.
        green_hiring_count = 0.
        purple_hiring_count = 0.
        green_count = 0
        purple_count = 0
        for s in self.subsession.in_previous_rounds():
            print("subsession " + str(s))
            for g in s.get_groups():
                print("group " + str(g) + ", g.worker_color=" + str(g.worker_color) + ", g.worker_invest=" + str(
                    g.worker_invest) + ", g.firm_hire=" + str(g.firm_hire))
                if g.worker_color == 'GREEN':
                    green_count += 1
                    if g.worker_invest:
                        green_invest_count += 1
                        print("green_invest_count=" + str(green_invest_count))
                    if g.firm_hire:
                        green_hiring_count += 1
                        print("green_hiring_count=" + str(green_hiring_count))
                elif g.worker_color == 'PURPLE':
                    purple_count += 1
                    if g.worker_invest:
                        purple_invest_count += 1
                        print("purple_invest_count=" + str(purple_invest_count))
                    if g.firm_hire:
                        purple_hiring_count += 1
                        print("purple_hiring_count=" + str(purple_hiring_count))
        if green_count == 0:
            green_count = 1
        if purple_count == 0:
            purple_count = 1

        self.group.green_invest_rate_shown = str(round(green_invest_count / green_count, 2))
        self.group.purple_invest_rate_shown = str(round(purple_invest_count / purple_count, 2))
        self.group.green_hire_rate_shown = str(round(green_hiring_count / green_count, 2))
        self.group.purple_hire_rate_shown = str(round(purple_hiring_count / purple_count, 2)) 
        self.group.avg_hire_rate_shown = str(round((purple_hiring_count + green_hiring_count)/(green_count+purple_count), 2))
        self.group.avg_invest_rate_shown = str(round((purple_invest_count + green_invest_count)/(green_count+purple_count) , 2))
        print("views.Worker:  group=" + str(self.group) + ", self.group.worker_color=" + str(self.group.worker_color))

        # table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
        # table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
        #                                           str(C.FIRM_HIRE_NOT_INVEST))
        # table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
        #                                               str(C.FIRM_NOT_HIRE_INVEST))
        # table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
        #                                              str(C.FIRM_NOT_HIRE_NOT_INVEST))
        second_stage_start = self.subsession.num_first_stage_rounds
        # if third_stage_start < self.subsession.round_number <= fourth_stage_start and self.group.worker_color == 'PURPLE':
        #     table_invest_hire = "{0} - c, {1} + s".format(str(C.WORKER_HIRE_INVEST),
        #                                                   str(C.FIRM_HIRE_INVEST))
        #     table_not_invest_hire = "{0}, {1} + s".format(str(C.WORKER_HIRE_NOT_INVEST),
        #                                                   str(C.FIRM_HIRE_NOT_INVEST))

        green_cost = 0
        purple_cost = 0
        extra_text_green = ""
        extra_text_purple = ""
        worker_send_signal = ""
        worker_reveal_type = ""

        stage_num = 0
        if 0 < self.round_number <= second_stage_start/2:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.HIGH_COST_OF_TRAINING
            stage_num = 1
            stage_round = self.round_number
            extra_text_type = "您配對到 " + str(self.group.worker_color) + " 的求職者。"
        elif second_stage_start/2 < self.round_number <= second_stage_start:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.LOW_COST_OF_TRAINING
            stage_num = 1
            stage_round = self.round_number
            extra_text_type = "您配對到 " + str(self.group.worker_color) + " 的求職者。"
        elif second_stage_start < self.round_number:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.LOW_COST_OF_TRAINING
            stage_num = 2
            stage_round = self.round_number - second_stage_start

            
        if second_stage_start < self.round_number and self.session.config['costly_signaling']:
            worker_choose_send = self.group.send_signal
            if worker_choose_send:
                worker_send_signal= "您決定傳送<b>「我願意投入受訓」</b>之訊息（訊息成本為 100 法幣） 。"             
                table_invest_hire = "{0} - c - 100, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
                table_not_invest_hire = "{0} - 100, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
                table_invest_not_hire = "{0} - c - 100, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
                table_not_invest_not_hire = "{0} - 100,{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
            else:
                worker_send_signal= "您決定<b>不傳送訊息</b>（訊息成本為 100 法幣） 。"            
                table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
                table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
                table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
                table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
        else:
            worker_choose_send = ""         
            table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
            table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
            table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
            table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))

        
        if second_stage_start < self.round_number and self.session.config['type_disclosure']:
            worker_choose_reveal = self.group.reveal_type
            if worker_choose_reveal:
                worker_reveal_type= "您決定<b>揭露</b>您的類別。"
            else:
                worker_reveal_type= "您決定<b>不揭露</b>您的類別。"
        else:
            worker_choose_reveal = ""
            worker_reveal_type = ""
        
        return {
            'table_invest_hire': str(table_invest_hire),
            'table_invest_not_hire': str(table_invest_not_hire),
            'table_not_invest_hire': str(table_not_invest_hire),
            'table_not_invest_not_hire': str(table_not_invest_not_hire),
            'green_invest_rate': self.group.green_invest_rate_shown,
            'purple_invest_rate': self.group.purple_invest_rate_shown,
            'green_hiring_rate': self.group.green_hire_rate_shown,
            'purple_hiring_rate': self.group.purple_hire_rate_shown,
            'worker_choose_reveal': worker_choose_reveal,
            'worker_reveal_type': str(worker_reveal_type),
            'worker_choose_send': worker_choose_send,
            'worker_send_signal': str(worker_send_signal),
            'avg_hiring_rate': self.group.avg_hire_rate_shown,
            'avg_invest_rate': self.group.avg_invest_rate_shown,
            'green_invest_count': str(green_invest_count),
            'purple_invest_count': str(purple_invest_count),
            'green_hiring_count': str(green_hiring_count),
            'purple_hiring_count': str(purple_hiring_count),
            'worker_color': str(self.group.worker_color),
            'cost_of_training': str(self.group.cost_of_training),
            'purple_cost': str(purple_cost),
            'green_cost': str(green_cost),
            'extra_text_green': str(extra_text_green),
            'extra_text_purple': str(extra_text_purple),
            'stage_num': str(stage_num),
            'stage_round': str(stage_round),
            'right_side_amounts': range(0, 11, 1),
        }



class Firm(Page):
    form_model = 'group'

    def get_form_fields(self):
        if self.subsession.use_firm_belief_elicitation:
            return ['firm_hire', 'firm_investment_belief']
        else:
            return ['firm_hire']

    def vars_for_template(self):

        green_invest_count = 0.
        purple_invest_count = 0.
        green_hiring_count = 0.
        purple_hiring_count = 0.
        green_count = 0
        purple_count = 0
        for s in self.subsession.in_previous_rounds():          
            for g in s.get_groups():               
                if g.worker_color == 'GREEN':
                    green_count += 1
                    if g.worker_invest:
                        green_invest_count += 1                    
                    if g.firm_hire:
                        green_hiring_count += 1                       
                elif g.worker_color == 'PURPLE':
                    purple_count += 1
                    if g.worker_invest:
                        purple_invest_count += 1                        
                    if g.firm_hire:
                        purple_hiring_count += 1                        
        if green_count == 0:
            self.group.green_invest_rate_shown = '0.0'
            self.group.green_hire_rate_shown = '0.0'
        else:
            self.group.green_invest_rate_shown = str(round(green_invest_count / green_count, 2))
            self.group.green_hire_rate_shown = str(round(green_hiring_count / green_count, 2))

        if purple_count == 0:
            self.group.purple_invest_rate_shown = '0.0'
            self.group.purple_hire_rate_shown = '0.0'
        else:
            self.group.purple_invest_rate_shown = str(round(purple_invest_count / purple_count, 2))
            self.group.purple_hire_rate_shown = str(round(purple_hiring_count / purple_count, 2))
          
            
        if purple_count + green_count == 0:
            self.group.avg_hire_rate_shown = '0.0'
            self.group.avg_invest_rate_shown = '0.0'
        else:
            self.group.avg_hire_rate_shown = str(round((purple_hiring_count + green_hiring_count)/(green_count+purple_count) , 2))
            self.group.avg_invest_rate_shown = str(round((purple_invest_count + green_invest_count)/(green_count+purple_count) , 2))
            

        second_stage_start = self.subsession.num_first_stage_rounds
        # third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        # fourth_stage_start = (
        #     self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        if second_stage_start < self.subsession.round_number <= fourth_stage_start and self.group.worker_color == 'PURPLE':
            table_invest_hire = "{0} - c, {1} + s".format(str(C.WORKER_HIRE_INVEST),
                                                          str(C.FIRM_HIRE_INVEST))
            table_not_invest_hire = "{0}, {1} + s".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                          str(C.FIRM_HIRE_NOT_INVEST))

        green_cost = 0
        purple_cost = 0
        extra_text_green = ""
        extra_text_purple = ""
        extra_text_type = ""
        firm_see_signal = ""
        firm_see_type = ""
        instructions_text = ""
        instructions_text_2 = ""
        instructions_text_3 = ""

        stage_num = 0
        if 0 < self.round_number <= second_stage_start/2:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.HIGH_COST_OF_TRAINING
            stage_num = 1
            stage_round = self.round_number
            extra_text_type = "您配對到 " + str(self.group.worker_color) + " 的求職者。"
        elif second_stage_start/2 < self.round_number <= second_stage_start:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.LOW_COST_OF_TRAINING
            stage_num = 1
            stage_round = self.round_number
            extra_text_type = "您配對到 " + str(self.group.worker_color) + " 的求職者。"
        elif second_stage_start < self.round_number:
            green_cost = C.LOW_COST_OF_TRAINING
            purple_cost = C.LOW_COST_OF_TRAINING
            stage_num = 2
            stage_round = self.round_number - second_stage_start
        # elif fourth_stage_start < self.round_number <= self.subsession.num_rounds:
        #     green_cost = C.FOURTH_COST_OF_TRAINING
        #     purple_cost = C.FOURTH_COST_OF_TRAINING
        #     stage_num = 4
        #     stage_round = self.round_number - fourth_stage_start
            
        if second_stage_start < self.round_number and self.session.config['costly_signaling']:            
            worker_choose_send = self.group.send_signal
            if worker_choose_send:
                firm_see_signal= "您配對到的求職者傳送<b>「我願意投入受訓」</b>之訊息（訊息成本為 100 法幣） 。"
                table_invest_hire = "{0} - c - 100, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
                table_not_invest_hire = "{0} - 100, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
                table_invest_not_hire = "{0} - c - 100, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
                table_not_invest_not_hire = "{0}-100,{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
            else:
                firm_see_signal= "您配對到的求職者<b>未傳送訊息</b>（訊息成本為 100 法幣） 。"
                table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
                table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
                table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
                table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))

        else:
            worker_choose_send = ""
            firm_see_signal = ""
            table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
            table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
            table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
            table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
        
        if second_stage_start < self.round_number and self.session.config['type_disclosure']:            
            worker_choose_reveal = self.group.reveal_type
            if worker_choose_reveal:      
                if self.group.worker_color == 'GREEN':  
                    firm_see_type= "您配對到的求職者揭露其類別為 <b>GREEN</b> 。"
                else:
                    firm_see_type= "您配對到的求職者揭露其類別為 <b>PURPLE</b> 。"
            else:
                firm_see_type= "您配對到的求職者<b>未揭露其類別</b>。"

        else:
            worker_choose_reveal = ""
            firm_see_type = ""
            
        return {
            'table_invest_hire': str(table_invest_hire),
            'table_invest_not_hire': str(table_invest_not_hire),
            'table_not_invest_hire': str(table_not_invest_hire),
            'table_not_invest_not_hire': str(table_not_invest_not_hire),
            'green_invest_rate': self.group.green_invest_rate_shown,
            'purple_invest_rate': self.group.purple_invest_rate_shown,
            'green_hiring_rate': self.group.green_hire_rate_shown,
            'purple_hiring_rate': self.group.purple_hire_rate_shown,
            'green_invest_count': str(green_invest_count),
            'purple_invest_count': str(purple_invest_count),
            'green_hiring_count': str(green_hiring_count),
            'purple_hiring_count': str(purple_hiring_count),
            'worker_choose_reveal': worker_choose_reveal,
            'firm_see_type': firm_see_type,
            'worker_choose_send': worker_choose_send,
            'firm_see_signal': firm_see_signal,
            'avg_hiring_rate': self.group.avg_hire_rate_shown,
            'avg_invest_rate': self.group.avg_invest_rate_shown,
            'worker_color': str(self.group.worker_color),
            'cost_of_training': str(self.group.cost_of_training),
            'graph_purple_invest_rate': safe_json(self.group.purple_invest_rate_shown),
            'graph_green_invest_rate': safe_json(self.group.green_invest_rate_shown),
            'graph_purple_hiring_rate': safe_json(self.group.purple_hire_rate_shown),
            'graph_green_hiring_rate': safe_json(self.group.green_hire_rate_shown),
            'purple_cost': str(purple_cost),
            'green_cost': str(green_cost),
            'extra_text_green': str(extra_text_green),
            'extra_text_purple': str(extra_text_purple),
            'extra_text_type': str(extra_text_type),
            'stage_num': str(stage_num),
            'stage_round': str(stage_round), 
            'right_side_amounts': range(0, 11, 1)
        }

    def is_displayed(self):
        return self.player.id_in_group == 2 and self.round_number <= self.subsession.num_rounds


class Instructions(Page):    
    form_model = '' 
    form_fields = []
    def is_displayed(self):
        second_stage_start = self.subsession.num_first_stage_rounds
        # third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        # fourth_stage_start = (
        #     self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        return self.round_number == 1 or self.round_number == 1+self.subsession.num_first_stage_rounds 
        # or self.round_number == 1+self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds or self.round_number == 1+self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds

    def vars_for_template(self):

        instructions_text = ""
        instructions_text_2 = ""
        instructions_text_3 = ""
        instructions_text_4 = ""
        second_stage_start = self.subsession.num_first_stage_rounds
        # third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        # fourth_stage_start = (
        #     self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        if self.round_number == 1:
                instructions_text = "您即將進入實驗的第一階段。"
                instructions_text_2 = "本階段的第 1 回合至第 10 回合， GREEN 求職者的受訓成本為 200 法幣 (c = 200)，PURPLE 求職者的受訓成本為 600 法幣 (c = 600)。" 
                instructions_text_3 = "本階段的第 11 回合至第 20 回合， GREEN 求職者的受訓成本為 200 法幣 (c = 200)，PURPLE 求職者的受訓成本為 200 法幣 (c = 200)。"   
                instructions_text_4 = "本階段雇主<b>可以看見</b>配對到的求職者之類別。"  
        elif self.round_number == 1+self.subsession.num_first_stage_rounds:
                instructions_text = "您即將進入實驗的第二階段。"
                instructions_text_2 = "本階段 GREEN 求職者的受訓成本為 200 法幣 (c = 200)，PURPLE 求職者的受訓成本為 200 法幣 (c = 200)"
                if self.subsession.treatment == 11:
                    instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以決定主動<b>揭露</b>其類別，亦可傳送<b>「我願意投入受訓」<b>的訊息，訊息成本為 100 法幣。"
                elif self.subsession.treatment == 10:
                    instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以決定主動<b>揭露</b>其類別。"
                elif self.subsession.treatment == 1:
                    instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以傳送<b>「我願意投入受訓」的</b>訊息，訊息成本為 100 法幣。"
                else:
                    instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。"

        # elif self.round_number == 1+self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds:
        #         instructions_text = "您即將進入實驗的第三階段。"
        #         instructions_text_2 = "本階段所有求職者的受訓成本為 200 法幣 (c = 200)。"
        #         if self.subsession.treatment == 11:
        #             instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以決定主動<b>揭露</b>其類別，亦可傳送<b>「我願意投入受訓」<b>的訊息，訊息成本為 100 法幣。"
        #         elif self.subsession.treatment == 10:
        #             instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以決定主動<b>揭露</b>其類別。"
        #         elif self.subsession.treatment == 1:
        #             instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以傳送<b>「我願意投入受訓」的</b>訊息，訊息成本為 100 法幣。"
        #         else:
        #             instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。"
        # elif self.round_number == 1+self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds:            
        #         instructions_text = "您即將進入實驗的第四階段。"
        #         instructions_text_2 = "本階段所有求職者的受訓成本為 200 法幣 (c = 200)。"
        #         if self.subsession.treatment == 11:
        #             instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以決定主動<b>揭露</b>其類別，亦可傳送<b>「我願意投入受訓」<b>的訊息，訊息成本為 100 法幣。"
        #         elif self.subsession.treatment == 10:
        #             instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以決定主動<b>揭露</b>其類別。"
        #         elif self.subsession.treatment == 1:
        #             instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。求職者可以傳送<b>「我願意投入受訓」的</b>訊息，訊息成本為 100 法幣。"
        #         else:
        #             instructions_text_3 = "本階段雇主<b>不會看見</b>配對到的求職者之類別。"        

        return {
            'instructions_text': instructions_text,
            'instructions_text_2': instructions_text_2,
            'instructions_text_3': instructions_text_3
            'instructions_text_4': instructions_text_4
        }

class TaskWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds
    title_text = ""
    body_text = "正在計算報酬..."
    def after_all_players_arrive(self):
        # Iterate through all groups and call set_payoffs
        self.group.set_payoffs()
        for player in self.subsession.get_players():
            player.set_payoffs()
    
class ResultsWaitPage(WaitPage):
    wait_for_all_players = True
    title_text = ""
    body_text = "請稍待其他人，謝謝！"
    def after_all_players_arrive(self):
        self.group.set_payoffs()
        for player in self.group.get_players():
            player.set_payoffs()
            if self.round_number >= 2:
                last_round_player = player.in_round(self.round_number - 1)
                player.computer_num = last_round_player.computer_num            



class SessionWideWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = ""
    body_text = "請稍待其他人，謝謝！"    

        
class Results(Page):
    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds
    def vars_for_template(self):
        second_stage_start = self.subsession.num_first_stage_rounds
        # third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        # fourth_stage_start = (
        #     self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)

        if 0 < self.round_number <= second_stage_start:
            stage_num = 1
            stage_round = self.round_number
        elif second_stage_start < self.round_number :
            stage_num = 2
            stage_round = self.round_number - second_stage_start
        # elif third_stage_start < self.round_number <= fourth_stage_start:
        #     stage_num = 3
        #     stage_round = self.round_number - third_stage_start
        # elif fourth_stage_start < self.round_number <= self.subsession.num_rounds:
        #     stage_num = 4
        #     stage_round = self.round_number - fourth_stage_start
        your_decision = ""
        their_decision = ""  
        your_payoff = ""
        their_payoff = ""  
        if self.player.id_in_group == 1:
            your_payoff = "您於本回合的應徵聘僱決策獲得 "+  str(self.group.worker_normal_payoff)+"。"
            their_payoff = "雇主於本回合的應徵聘僱決策獲得 "+str(self.group.firm_normal_payoff)+"。"
            if self.group.firm_hire:
                their_decision = "雇主決定<b>錄取</b>。"
            else: 
                their_decision = "雇主決定<b>不錄取</b>。"
            if self.group.worker_invest:
                your_decision = "您決定<b>受訓</b>。"
            else: 
                your_decision = "您決定<b>不受訓</b>。"
        elif self.player.id_in_group == 2:
            your_payoff = "您於本回合的應徵聘僱決策獲得 "+  str(self.group.firm_normal_payoff)+"。"
            their_payoff = "求職者於本回合的應徵聘僱決策獲得 "+str(self.group.worker_normal_payoff)+"。"
            if self.group.firm_hire:
                your_decision = "您決定<b>錄取</b>。"
            else: 
                your_decision = "您決定<b>不錄取</b>"
            if self.group.worker_invest:
                their_decision = "您配對到 "+str(self.group.worker_color)+" 求職者，求職者決定<b>受訓</b>。"
            else: 
                their_decision = "您配對到 "+str(self.group.worker_color)+" 求職者，求職者決定<b>不受訓</b>。"
        return {
            'firm_normal_payoff': str(self.group.firm_normal_payoff),      
            'worker_normal_payoff': str(self.group.worker_normal_payoff),
            'stage_num': str(stage_num),
            'stage_round': str(stage_round),
            'worker_color': str(self.group.worker_color),
            'your_decision': your_decision,
            'their_decision': their_decision,
            'your_payoff': your_payoff,
            'their_payoff': their_payoff
        }

class Task_Intro(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds
    def vars_for_template(self):
        task_instructions_text_1 = "主要實驗已結束，接下來請您完成兩個額外項目。"
        task_instructions_text_2 = "實驗結束後電腦會隨機選取其中一個項目實現報酬，並將您於該項目獲得的法幣換算成新台幣加到最終報酬。"
        return {
            'task_instructions_text_1': task_instructions_text_1,
            'task_instructions_text_2': task_instructions_text_2
        }

class Task_1(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds     
    form_model = 'player'
    form_fields = ['task_1']

class Task_2(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds
    form_model = 'player'
    form_fields = ['task_2']

class Payoffs(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds
    def vars_for_template(self):
        paying_round = self.player.paying_round
        belief_round = self.player.belief_round
        choose_row = self.player.lottery_1/10
        choose_task = self.player.choose_task
        task_payoff = self.player.task_payoff
        normal_payoff = self.player.final_normal_payoff
        belief_payoff = self.player.belief_payoff
        participation_fee = self.session.config['participation_fee']
        normal_into_currency = normal_payoff/7
        task_into_currency = task_payoff/7
        belief_into_currency = belief_payoff/7
        total_payoff = self.player.total_payoff

        return {
            'participation_fee': f'{participation_fee:.0f}',
            'total_payoff': f'{total_payoff:.0f}',
            'task_payoff': str(task_payoff),
            'choose_task': str(choose_task),
            'paying_round': str(paying_round),
            'belief_round': str(belief_round),
            'task_into_currency': f'{task_into_currency:.0f}',           
            'task_payoff': str(task_payoff),
            'normal_payoff': str(normal_payoff),  
            'belief_payoff': str(belief_payoff),
            'belief_into_currency': f'{belief_into_currency:.0f}',
            'normal_into_currency': f'{normal_into_currency:.0f}',
            'choose_row': f'{choose_row:.0f}'
        }

page_sequence = [
    Computer_Number,
    Begin_Experiment,
    SessionWideWaitPage,
    Instructions,
    Reveal_Signal,
    WaitForWorkers,
    Worker,
    Firm,
    ResultsWaitPage,
    Results,    
    Task_Intro,
    Task_1,
    Task_2,
    TaskWaitPage,
    Payoffs
]