from dataclasses import dataclass

class Rank:
    # 构造函数，用于初始化对象的属性
    def __init__(self, clan_name, leader_name,damage,rank,delta_damage):
        self.clan_name = clan_name
        self.leader_name = leader_name
        self.damage = damage
        self.rank = rank
        self.delta_damage = delta_damage

    # 方法：描述对象的行为
    def __str__(self):
        return (f"公会名称: {self.clan_name} \n "
                f"会长名: {self.leader_name} \n"
                f"公会排名: {self.rank} \n"
                f"公会总伤害:{self.damage}")

    @dataclass
    class Rank:
        clan_name: str
        leader_name: str
        damage:str
        rank:str
        delta_damage: str
# 创建一个类的实例
# person1 = Person("Alice", 30)
#
# # 访问对象的属性和方法
# print(person1.name)  # 输出: Alice
# print(person1.age)   # 输出: 30
# print(person1.greet())  # 输出: Hello, my name is Alice and I am 30 years old.
