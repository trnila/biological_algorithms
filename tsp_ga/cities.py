from collections import namedtuple

City = namedtuple('City', ['x', 'y', 'name', 'id'])
cities = [
    City(60,200, 'A',0),
    City(80,200,'B',1),
    City(80,180,'C',2),
    City(140,180,'D',3),
    City(20,160,'E',4),
    City(100,160,'F',5),
    City(200,160,'G',6),
    City(140,140,'H',7),
    City(40,120,'I',8),
    City(100,120,'J',9),
    City(180,100, 'K',10),
    City(60,80, 'L',11),
    City(120,80, 'M',12),
    City(180,60,'N',13),
    City(20,40,'O',14),
    City(100,40,'P',15),
    City(200,40,'Q',16),
    City(20,20,'R',17),
    City(60,20,'S',18),
    City(160,20,'T',19),
]