# -*- coding: utf-8 -*-
from game.autoenv import EventHandler, user_input, Game
from .baseclasses import Character, register_character
from ..actions import DropCards, Fatetell, FatetellAction
from ..cards import Card, RedUFOSkill, Skill, t_None, BaseAttack, InevitableAttack
from ..inputlets import ChooseOptionInputlet, ChoosePeerCardInputlet
from utils import classmix


class AssaultSkill(RedUFOSkill):
    increment = 1


class FreakingPowerSkill(Skill):
    associated_action = None
    target = t_None


class FreakingPower(FatetellAction):
    def __init__(self, atkact):
        self.atkact = atkact
        self.source = atkact.source
        self.target = atkact.target

    def apply_action(self):
        act = self.atkact
        src = act.source
        ft = Fatetell(src, lambda c: c.suit in (Card.HEART, Card.DIAMOND))
        g = Game.getgame()
        if g.process_action(ft):
            act.__class__ = classmix(InevitableAttack, act.__class__)
        else:
            act.yugifptag = True
        return True


class YugiHandler(EventHandler):
    def handle(self, evt_type, act):
        if evt_type == 'action_before' and isinstance(act, BaseAttack) and not hasattr(act, 'yugifptag'):
            src = act.source
            if not src.has_skill(FreakingPowerSkill): return act
            if not user_input([src], ChooseOptionInputlet(self, (False, True))):
                return act
            tgt = act.target
            Game.getgame().process_action(FreakingPower(act))

        elif evt_type == 'action_after' and hasattr(act, 'yugifptag'):
            if not act.succeeded: return act
            src = act.source; tgt = act.target
            g = Game.getgame()
            catnames = ('cards', 'showncards', 'equips')
            card = user_input([src], ChoosePeerCardInputlet(self, tgt, catnames))
            if card:
                g.players.exclude(tgt).reveal(card)
                g.process_action(DropCards(tgt, [card]))

        return act


@register_character
class Yugi(Character):
    skills = [AssaultSkill, FreakingPowerSkill]
    eventhandlers_required = [YugiHandler]
    maxlife = 4
