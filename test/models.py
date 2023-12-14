#-*- coding: utf-8 -*-
from __future__ import division

import random
import math

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

# author = 'crabbe@hss.caltech.edu'

doc = """
Workers choose whether to invest in training.  Firms can observe the "Color" of workers and decides whether to hire the
worker they are (randomly and anonymously) paired with, then asked how likely it is the worker chose to invest in
training.
"""


class C(BaseConstants):
    NAME_IN_URL = 'test'
    # number of players in a group - should be a multiple of 2 (6)
    PLAYERS_PER_GROUP = 2
    # the number of rounds to play - should be a multiple of 4
    NUM_ROUNDS = 40
    FIRST_COST_OF_TRAINING_GREEN = 200
    FIRST_COST_OF_TRAINING_PURPLE = 600
    SECOND_COST_OF_TRAINING = 200
    THIRD_COST_OF_TRAINING = 200
    FOURTH_COST_OF_TRAINING = 200
    SIGNALING_COST = 10
    WORKER_HIRE_INVEST = 1800
    WORKER_HIRE_NOT_INVEST = 1400
    WORKER_NOT_HIRE_INVEST = 1000
    WORKER_NOT_HIRE_NOT_INVEST = 1200
    FIRM_HIRE_INVEST = 1600
    FIRM_HIRE_NOT_INVEST = 400
    FIRM_NOT_HIRE_INVEST = 1200
    FIRM_NOT_HIRE_NOT_INVEST = 1200
    COLORS = ["PURPLE", "GREEN"]


class Subsession(BaseSubsession):
    green_investment_count = models.IntegerField(initial=0)
    purple_investment_count = models.IntegerField(initial=0)
    green_hiring_count = models.IntegerField(initial=0)
    purple_hiring_count = models.IntegerField(initial=0)
    is_final_round = models.BooleanField(initial=False)
    use_firm_belief_elicitation = models.BooleanField(initial=True)
    use_worker_belief_elicitation = models.BooleanField(initial=True)
    num_first_stage_rounds = models.IntegerField(initial=0)
    num_second_stage_rounds = models.IntegerField(initial=0)
    num_third_stage_rounds = models.IntegerField(initial=0)
    num_fourth_stage_rounds = models.IntegerField(initial=0)
    num_rounds = models.IntegerField(initial=0)
    treatment = models.IntegerField(initial=-1)
    
    def creating_session(self):
        self.group_randomly(fixed_id_in_group=True)
    # If the current round number is 1, this conditional statement proceeds to create a map that associates round numbers
    # with a boolean value indicating whether it's a paid round or not. This mapping is stored in the variable self.paying_round,
    # and it's generated randomly between rounds 1 and C.NUM_ROUNDS.
    # The subsequent if statements check for certain configuration options in the self.session.config dictionary. If a configuration option is found, it's assigned to the respective class attribute. For example, self.use_firm_belief_elicitation and self.use_worker_belief_elicitation are set based on the presence of 'use_firm_belief_elicitation' and 'use_worker_belief_elicitation' in the session configuration. Similar checks are done for other parameters like the number of rounds in different stages (self.num_first_stage_rounds, self.num_second_stage_rounds, etc.) for the third stage.
        if 'use_firm_belief_elicitation' in self.session.config:
            self.use_firm_belief_elicitation = self.session.config['use_firm_belief_elicitation']

        if 'use_worker_belief_elicitation' in self.session.config:
            self.use_worker_belief_elicitation = self.session.config['use_worker_belief_elicitation']
        
        if 'type_disclosure' in self.session.config and 'costly_signaling'in self.session.config:
            if self.session.config['type_disclosure']:
                if self.session.config['costly_signaling']:
                    self.treatment = 11
                else:
                    self.treatment = 10
            else:
                if self.session.config['costly_signaling']:
                    self.treatment = 1
                else:
                    self.treatment = 0

        if 'num_first_stage_rounds' in self.session.config:
            self.num_first_stage_rounds = self.session.config['num_first_stage_rounds']
        else:
            self.num_first_stage_rounds = 1

        if 'num_second_stage_rounds' in self.session.config:
            self.num_second_stage_rounds = self.session.config['num_second_stage_rounds']
        else:
            self.num_second_stage_rounds = 1

        if 'num_third_stage_rounds' in self.session.config:
            self.num_third_stage_rounds = self.session.config['num_third_stage_rounds']
        else:
            self.num_third_stage_rounds = 1

        if 'num_fourth_stage_rounds' in self.session.config:
            self.num_fourth_stage_rounds = self.session.config['num_fourth_stage_rounds']
        else:
            self.num_fourth_stage_rounds = 1

        self.num_rounds = self.num_first_stage_rounds + self.num_second_stage_rounds + self.num_third_stage_rounds \
                          + self.num_fourth_stage_rounds

        # assign the players into groups, make it so that players with even IDs are always
        # workers and odd IDs are always firms
        if self.round_number > 0:
            odd_players = []
            even_players = []
            for p in self.get_players():
                if p.participant.id_in_session % 2 == 0:
                    even_players.append(p)
                else:
                    odd_players.append(p)
            list_of_lists = []
            random.shuffle(odd_players)
            random.shuffle(even_players)
            num_groups = int(len(self.get_players()) / C.PLAYERS_PER_GROUP)
            for g in range(num_groups):
                group_players = [odd_players[g], even_players[g]]
                print("groupnum " + str(g) + ": " + str(group_players))
                list_of_lists.append(group_players)
                self.get_group_matrix(list_of_lists)

        # if this is the first round, assign a color to the worker (so that there are even number of each color)
        # and store them in participant.vars so that they can be accessed by the group

        if self.round_number == 1:
            for player in self.get_players():
                player.paying_round = random.randint(1, self.num_rounds)
                player.lottery_1 = random.choice(range(10, 101, 10))
                player.lottery_2 = random.randint(0, 9)
                player.lottery_3 = random.randint(1, 100)
                player.choose_task = random.randint(1, 2)
                player.risk_1 = random.randint(1, 2)
                player.risk_2 = random.randint(1, 10)
                player.belief_round = random.choice([round_num for round_num in range(1, self.num_rounds + 1) if round_num != player.paying_round])
            count = 0
            color_list = []
            for g in self.get_groups():
                count += 1
                if count % 3 == 1:
                    color_list.append(C.COLORS[0])  # Append 'PURPLE'
                else:
                    color_list.append(C.COLORS[1])  # Append 'GREEN'
            random.shuffle(color_list)
            count = 0

            for g in self.get_groups():
                g.get_player_by_role('Worker').participant.vars['worker_color'] = color_list[count]
                count += 1
                print(
                    "round_number=" + str(self.round_number) + ", assigning group " + str(
                        g) + " worker color value " + str(
                        g.get_player_by_role('Worker').participant.vars['worker_color']))
        # retrieve the worker_color set for this group's worker in round 1
        elif self.round_number > 1:            
            for player in self.get_players():
                # Use values from the previous round
                last_round_player = player.in_round(self.round_number - 1)
                player.paying_round = last_round_player.paying_round
                player.lottery_1 = last_round_player.lottery_1
                player.lottery_2 = last_round_player.lottery_2
                player.lottery_3 = last_round_player.lottery_3
                player.choose_task = last_round_player.choose_task
                player.risk_1 = last_round_player.risk_1
                player.risk_2 = last_round_player.risk_2
                player.belief_round = last_round_player.belief_round
        for g in self.get_groups():
            g.worker_color = g.get_player_by_role('Worker').participant.vars['worker_color']
      

        # set up the correct payoff vars and cost_of_training for each group (based on treatment and worker color)
        third_stage_start = (self.num_first_stage_rounds + self.num_second_stage_rounds)
        fourth_stage_start = (self.num_first_stage_rounds + self.num_second_stage_rounds + self.num_third_stage_rounds)
        for g in self.get_groups():
            g.round_num = self.round_number
            g.use_firm_belief = self.use_firm_belief_elicitation
            g.use_worker_belief = self.use_worker_belief_elicitation
            if 0 < self.round_number <= self.num_first_stage_rounds:
                if g.worker_color == 'GREEN':
                    g.cost_of_training = C.FIRST_COST_OF_TRAINING_GREEN
                elif g.worker_color == 'PURPLE':
                    g.cost_of_training = C.FIRST_COST_OF_TRAINING_PURPLE
            elif self.num_first_stage_rounds < self.round_number <= third_stage_start:
                g.cost_of_training = C.SECOND_COST_OF_TRAINING
            elif third_stage_start < self.round_number <= fourth_stage_start:
                g.cost_of_training = C.THIRD_COST_OF_TRAINING               
            elif fourth_stage_start < self.round_number <= self.num_rounds:
                g.cost_of_training = C.FOURTH_COST_OF_TRAINING               

class Player(BasePlayer):
    def role(self):
        if self.id_in_group == 1:
            return 'Worker'
        if self.id_in_group == 2:
            return 'Firm'
    lottery_1 = models.IntegerField(initial=None)
    lottery_2 = models.IntegerField(initial=None)
    lottery_3 = models.IntegerField(initial=None)
    choose_task = models.IntegerField(initial=None)
    risk_1 = models.IntegerField(initial=None)
    risk_2 = models.IntegerField(initial=None)
    paying_round = models.IntegerField(initial=None)
    belief_round = models.IntegerField(initial=None)
    computer_num = models.IntegerField(
        initial=None,
        verbose_name = '請實驗者輸入電腦編號，謝謝!',
        min = 1,
        max = 32,
    )
    task_1 = models.IntegerField(
        initial=None,
        verbose_name = '電腦給您 200 法幣，您必須決定要將多少法幣投入募資專案 A，該專案的達標機率為 50%。給定您決定投入 x 法幣，達標的話您將獲得 2.5x（即投入專案的法幣之 2.5 倍），沒達標的話您將獲得 0 法幣 。您會保有所有未投入專案的法幣，因此您於本項目的報酬會是未投入專案的法幣，加上投入該專案的收穫（如前所述，收穫可能為 0 ）。請問您要將多少法幣投入專案 A（請填入 0 至 200 的整數）?',
        min = 0,
        max = 200,
    )
    task_2 = models.IntegerField(
        verbose_name = '電腦給您 200 法幣，您必須決定要將多少法幣投入募資專案 B，該專案的達標機率為 40%。給定您決定投入 x 法幣，達標的話您將獲得 3x （即投入專案的法幣之 3 倍），沒達標的話您將獲得 0 法幣 。您會保有所有未投入專案的法幣，因此您於本項目的報酬會是未投入專案的法幣，加上投入該專案的收穫 （如前所述，收穫可能為 0 ）。請問您要將多少法幣投入專案 B（請填入 0 至 200 的整數）?',
        initial= None,
        min = 0,
        max = 200,
    )
    task_payoff = models.CurrencyField(
         initial=0,
    )
    final_normal_payoff = models.CurrencyField(
         initial=0,
    )
    total_payoff = models.CurrencyField(
         initial=0,
    )
    belief_payoff = models.CurrencyField(
         initial=0,
    )
    def set_payoffs(self):
        for player in self.group.get_players():
            belief_payoff = 0
            final_normal_payoff = 0
            task_payoff = 0         
            total_payoff = 0            
            if self.subsession.round_number == 1:        
                if self.belief_round == 1:
                    if player.role() == 'Worker':
                        if self.group.worker_hiring_belief > self.lottery_1:
                            if self.group.firm_hire:
                                self.belief_payoff = 200
                            else:
                                self.belief_payoff = 0
                        elif self.group.worker_hiring_belief <= self.lottery_1 and self.lottery_1 - self.group.worker_hiring_belief <= 9:
                            if self.group.worker_hiring_belief > self.lottery_1 - self.lottery_2:
                                if self.group.firm_hire:
                                    self.belief_payoff = 200
                                else:
                                    self.belief_payoff = 0                   
                            else:
                                if self.lottery_3 <= self.lottery_1 - self.lottery_2:
                                    self.belief_payoff = 200
                                else:
                                    self.belief_payoff = 0
                        else:
                            if self.lottery_3 <= self.lottery_1:
                                self.belief_payoff = 200
                            else:
                                self.belief_payoff = 0
                    else:
                        if self.group.firm_investment_belief > self.lottery_1:
                            if self.group.worker_invest:
                                self.belief_payoff = 200
                            else:
                                self.belief_payoff = 0
                        elif self.group.firm_investment_belief <= self.lottery_1 and self.lottery_1 - self.group.firm_investment_belief <= 9:
                            if self.group.firm_investment_belief > self.lottery_1 - self.lottery_2:
                                if self.group.worker_invest:
                                    self.belief_payoff = 200
                                else:
                                    self.belief_payoff = 0                   
                            else:
                                if self.lottery_3 <= self.lottery_1 - self.lottery_2:
                                    self.belief_payoff = 200
                                else:
                                    self.belief_payoff = 0 
                        else:
                            if self.lottery_3 <= self.lottery_1:
                                self.belief_payoff = 200
                            else:
                                self.belief_payoff = 0
                
                if self.paying_round == 1:
                    if player.role() == 'Worker':
                        self.final_normal_payoff = self.group.worker_normal_payoff
                    else:
                        self.final_normal_payoff = self.group.firm_normal_payoff
            elif self.subsession.round_number > 1:
                last_round_player = self.in_round(self.round_number - 1)
                if self.subsession.round_number == self.paying_round:
                    if player.role() == 'Firm':                 
                        self.final_normal_payoff = self.group.firm_normal_payoff
                    else:
                        self.final_normal_payoff = self.group.worker_normal_payoff
                elif self.subsession.round_number > self.paying_round:
                    self.final_normal_payoff = last_round_player.final_normal_payoff
                    
                if self.subsession.round_number == self.belief_round:
                    if player.role() == 'Worker':
                        if self.group.worker_hiring_belief > self.lottery_1:
                            if self.group.firm_hire:
                                self.belief_payoff = 200
                            else:
                                self.belief_payoff = 0
                        elif self.group.worker_hiring_belief <= self.lottery_1 and self.lottery_1 - self.group.worker_hiring_belief <= 9:
                            if self.group.worker_hiring_belief > self.lottery_1 - self.lottery_2:
                                if self.group.firm_hire:
                                    self.belief_payoff = 200
                                else:
                                    self.belief_payoff = 0                   
                            else:
                                if self.lottery_3 <= self.lottery_1 - self.lottery_2:
                                    self.belief_payoff = 200
                                else:
                                    self.belief_payoff = 0
                        else:
                            if self.lottery_3 <= self.lottery_1:
                                self.belief_payoff = 200
                            else:
                                self.belief_payoff = 0
                    else:
                        if self.group.firm_investment_belief > self.lottery_1:
                            if self.group.worker_invest:
                                self.belief_payoff = 200
                            else:
                                self.belief_payoff = 0
                        elif self.group.firm_investment_belief <= self.lottery_1 and self.lottery_1 - self.group.firm_investment_belief <= 9:
                            if self.group.firm_investment_belief > self.lottery_1 - self.lottery_2:
                                if self.group.worker_invest:
                                    self.belief_payoff = 200
                                else:
                                    self.belief_payoff = 0                   
                            else:
                                if self.lottery_3 <= self.lottery_1 - self.lottery_2:
                                    self.belief_payoff = 200
                                else:
                                    self.belief_payoff = 0 
                        else:
                            if self.lottery_3 <= self.lottery_1:
                                self.belief_payoff = 200
                            else:
                                self.belief_payoff = 0
                elif self.subsession.round_number > self.belief_round:
                    self.belief_payoff = last_round_player.belief_payoff            

            if self.subsession.round_number == self.subsession.num_rounds: 

                # if self.group.field_maybe_none('worker_task_1') is None or self.group.field_maybe_none('worker_task_2') is None: 
                #     self.task_payoff = 0
                # else:
                #     if player.role() == 'Worker' and self.choose_task == 1:
                #         if self.risk_1 == 1:                           
                #             self.task_payoff = self.group.worker_task_1 * 2.5 + 200 - self.group.worker_task_1
                #         else:
                #             self.task_payoff = 200 - self.group.worker_task_1
                #     elif player.role() == 'Worker' and self.choose_task == 2:
                #         if self.risk_2 <= 4: 
                #             self.task_payoff = self.group.worker_task_2 * 2.5 + 200 - self.group.worker_task_2
                #         else:                                                     
                #             self.task_payoff = 200 - self.group.worker_task_2
                #     elif player.role() == 'Firm' and self.choose_task == 1:            
                #         if self.risk_1 == 1:                           
                #             self.task_payoff = self.group.firm_task_1 * 2.5 + 200 - self.group.firm_task_1
                #         else:
                #             self.task_payoff = 200 - self.group.firm_task_1
                #     elif player.role() == 'Firm' and self.choose_task == 2:            
                #         if self.risk_2 <= 4:                           
                #             self.task_payoff = self.group.firm_task_2 * 2.5 + 200 - self.group.firm_task_2
                #         else:
                #             self.task_payoff = 200 - self.group.firm_task_2   
                if self.field_maybe_none('task_1') is None or self.field_maybe_none('task_2') is None: 
                    self.task_payoff = 0
                else:
                    if self.choose_task == 1:
                        if self.risk_1 == 1:                           
                            self.task_payoff = self.task_1 * 2.5 + 200 - self.task_1
                        else:
                            self.task_payoff = 200 - self.task_1
                    else:
                        if self.risk_2 <= 4: 
                            self.task_payoff = self.task_2 * 2.5 + 200 - self.task_2
                        else:                                                     
                            self.task_payoff = 200 - self.task_2                   
            if self.subsession.round_number == self.subsession.num_rounds:    
                self.total_payoff = (self.task_payoff + self.final_normal_payoff + self.belief_payoff)/7 +self.session.config['participation_fee']       

                
class Group(BaseGroup):
    send_signal = models.BooleanField(
        initial = None,
        doc="""Whether the worker wants to send costly message""",
        verbose_name='您要傳送<b>「我願意投入受訓」</b>的訊息給雇主嗎? 傳送訊息的成本為10法幣。',
        choices=[
            [True, '是'], 
            [False, '否'], 
        ],
    )
    reveal_type = models.BooleanField(
        initial = None,
        doc="""Whether the worker wants to reveal their type""",
        verbose_name='您要向雇主揭露您的類別嗎?',
        choices=[
            [True, '是'],  
            [False, '否'],  
        ],
    )
    worker_invest = models.BooleanField(
        initial = None,
        doc="""Whether the worker wants to invest""",
        verbose_name='您要投入受訓嗎?',
        choices=[
            [True, '是'],
            [False, '否'],
        ],
    )
    firm_hire = models.BooleanField(
        initial = None,
        doc="""Whether the firm wants to hire""",
        verbose_name='您要錄取求職者嗎?',
        choices=[
            [True, '是'],
            [False, '否'], 
        ],
    )
    firm_investment_belief = models.IntegerField(
        initial = None,
    )
    worker_hiring_belief = models.IntegerField(
        initial=None,     
    )  
    worker_normal_payoff = models.CurrencyField(
        initial=0,
    )
    firm_normal_payoff = models.CurrencyField(
        initial=0,
    )
    # firm_task_1 = models.IntegerField(
    #     initial=None,
    #     verbose_name = '電腦給您 200 法幣，您必須決定要將多少法幣投入募資專案 A，該專案的達標機率為 50%。給定您決定投入 x 法幣，達標的話您將獲得 2.5x（即投入專案的法幣之 2.5 倍），沒達標的話您將獲得 0 法幣 。您會保有所有未投入專案的法幣，因此您於本項目的報酬會是未投入專案的法幣，加上投入該專案的收穫（如前所述，收穫可能為 0 ）。請問您要將多少法幣投入專案 A（請填入 0 至 200 的整數）?',
    #     min = 0,
    #     max = 200,
    # )
    # firm_task_2 = models.IntegerField(
    #     verbose_name = '電腦給您 200 法幣，您必須決定要將多少法幣投入募資專案 B，該專案的達標機率為 40%。給定您決定投入 x 法幣，達標的話您將獲得 3x （即投入專案的法幣之 3 倍），沒達標的話您將獲得 0 法幣 。您會保有所有未投入專案的法幣，因此您於本項目的報酬會是未投入專案的法幣，加上投入該專案的收穫 （如前所述，收穫可能為 0 ）。請問您要將多少法幣投入專案 B（請填入 0 至 200 的整數）?',
    #     initial= None,
    #     min = 0,
    #     max = 200,
    # )    
    # worker_task_1 = models.IntegerField(
    #     initial=None,
    #     verbose_name = '電腦給您 200 法幣，您必須決定要將多少法幣投入募資專案 A，該專案的達標機率為 50%。給定您決定投入 x 法幣，達標的話您將獲得 2.5x（即投入專案的法幣之 2.5 倍），沒達標的話您將獲得 0 法幣 。您會保有所有未投入專案的法幣，因此您於本項目的報酬會是未投入專案的法幣，加上投入該專案的收穫（如前所述，收穫可能為 0 ）。請問您要將多少法幣投入專案 A（請填入 0 至 200 的整數）?',
    #     min = 0,
    #     max = 200,
    # )
    # worker_task_2 = models.IntegerField(
    #     verbose_name = '電腦給您 200 法幣，您必須決定要將多少法幣投入募資專案 B，該專案的達標機率為 40%。給定您決定投入 x 法幣，達標的話您將獲得 3x （即投入專案的法幣之 3 倍），沒達標的話您將獲得 0 法幣 。您會保有所有未投入專案的法幣，因此您於本項目的報酬會是未投入專案的法幣，加上投入該專案的收穫 （如前所述，收穫可能為 0 ）。請問您要將多少法幣投入專案 B（請填入 0 至 200 的整數）?',
    #     initial= None,
    #     min = 0,
    #     max = 200,
    # ) 


    worker_color = models.StringField()
    cost_of_training = models.IntegerField()
    # the current round number because you can't access that info from the Constants on the actual pages
    round_num = models.IntegerField()
    # whether or not to ask the firm for their belief of how likely the worker invested
    use_firm_belief = models.BooleanField()
    use_worker_belief = models.BooleanField()

    # the output should reveal the rates that the players see
    green_invest_rate_shown = models.StringField()
    purple_invest_rate_shown = models.StringField()
    green_hire_rate_shown = models.StringField()
    purple_hire_rate_shown = models.StringField()
    avg_invest_rate_shown =  models.StringField()
    avg_hire_rate_shown = models.StringField()

    def set_payoffs(self):
        firm = self.get_player_by_role('Firm')
        worker = self.get_player_by_role('Worker')     
        
        if self.field_maybe_none('send_signal') is None:                       
            if self.worker_invest and self.firm_hire:
                worker_normal_payoff = (C.WORKER_HIRE_INVEST - self.cost_of_training)
                firm_normal_payoff = (C.FIRM_HIRE_INVEST)
            elif self.worker_invest and not self.firm_hire:
                worker_normal_payoff = (C.WORKER_NOT_HIRE_INVEST - self.cost_of_training)
                firm_normal_payoff = (C.FIRM_NOT_HIRE_INVEST)
            elif not self.worker_invest and self.firm_hire:
                worker_normal_payoff = (C.WORKER_HIRE_NOT_INVEST)
                firm_normal_payoff = (C.FIRM_HIRE_NOT_INVEST)
            elif not self.worker_invest and not self.firm_hire:
                worker_normal_payoff = (C.WORKER_NOT_HIRE_NOT_INVEST)
                firm_normal_payoff = (C.FIRM_NOT_HIRE_NOT_INVEST)
        elif self.field_maybe_none('send_signal'):
            if self.worker_invest and self.firm_hire:
                worker_normal_payoff = (C.WORKER_HIRE_INVEST - self.cost_of_training-C.SIGNALING_COST)
                firm_normal_payoff = (C.FIRM_HIRE_INVEST)
            elif self.worker_invest and not self.firm_hire:
                worker_normal_payoff = (C.WORKER_NOT_HIRE_INVEST - self.cost_of_training-C.SIGNALING_COST)
                firm_normal_payoff = (C.FIRM_NOT_HIRE_INVEST)
            elif not self.worker_invest and self.firm_hire:
                worker_normal_payoff = (C.WORKER_HIRE_NOT_INVEST-C.SIGNALING_COST)
                firm_normal_payoff = (C.FIRM_HIRE_NOT_INVEST)
            elif not self.worker_invest and not self.firm_hire:
                worker_normal_payoff = (C.WORKER_NOT_HIRE_NOT_INVEST-C.SIGNALING_COST)
                firm_normal_payoff = (C.FIRM_NOT_HIRE_NOT_INVEST)
        else: 
            if self.worker_invest and self.firm_hire:
                worker_normal_payoff = (C.WORKER_HIRE_INVEST - self.cost_of_training)
                firm_normal_payoff = (C.FIRM_HIRE_INVEST)
            elif self.worker_invest and not self.firm_hire:
                worker_normal_payoff = (C.WORKER_NOT_HIRE_INVEST - self.cost_of_training)
                firm_normal_payoff = (C.FIRM_NOT_HIRE_INVEST)
            elif not self.worker_invest and self.firm_hire:
                worker_normal_payoff = (C.WORKER_HIRE_NOT_INVEST)
                firm_normal_payoff = (C.FIRM_HIRE_NOT_INVEST)
            elif not self.worker_invest and not self.firm_hire:
                worker_normal_payoff = (C.WORKER_NOT_HIRE_NOT_INVEST)
                firm_normal_payoff = (C.FIRM_NOT_HIRE_NOT_INVEST)        
        self.firm_normal_payoff = firm_normal_payoff
        self.worker_normal_payoff = worker_normal_payoff