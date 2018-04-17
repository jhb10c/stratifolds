from strat import *

###########Test if a graph is Horned Tree
G1=strat_graph()
edgs=[(1,'a',2),(3,'a'),(3,'c'),
      (2,'b',2),(4,'b'),(4,'c'),
      (5,'c'),(5,'d'),(6,'d'),(6,'e'),
      (8,'e',2),(7,'d'),(7,'f'),(9,'f',2)]
G1.addEdg(edgs)
print(G1.is_horned_tree())
G1.draw()

###########Test if a graph is 2,1-collapsible
G2=strat_graph()
edgs=[(1,'a',2),(1,'b',2),(2,'a'),(3,'b')]
G2.addEdg(edgs)
print(G2.is_21_collapsible())
G2.draw()

###########Test if a graph is trivalent and simply connected
G3=strat_graph()
edgs=[(1,'a',2),(2,'a'),(2,'b',2),(3,'b'),
      (3,'c',2),(4,'c'),(1,'d',2),(5,'d'),
      (5,'e',2),(6,'e'),(5,'f',2),(7,'f'),
      (7,'g',2),(7,'h',2),(7,'i',2),(8,'g'),
      (9,'h'),(10,'i'),
      (4,'j'),(11,'j'),(12,'j'),(12,'k'),
      (13,'k'),(13,'l'),(15,'l',2),(15,'n',2),
      (17,'n'),(14,'k'),(14,'m'),(16,'m',2),
      (16,'o',2),(16,'p',2),(18,'o'),(19,'p'),
      (19,'q'),(20,'q'),(21,'q')]
G3.addEdg(edgs)

print(G3.is_simply_connected())
G3.draw()


###########Perform operation O1
G4=b111(black='a',white=[0,1,2])
G4.draw()
G4_1=G4.O1(1,['a'],[])
G4_1.draw()


###########Perform operation O1_1

#Automatic naming for avoiding repeated names
W=get_int()
B=get_str()

G5=b111(black=next(B),white=[next(W) for i in range(3)])
G5.draw()
G6=b111(black=next(B),white=[next(W) for i in range(3)])
G6.draw()
G7=G5.O1_1(0,G6,3)
G7.draw()
