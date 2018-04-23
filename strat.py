import networkx as nx
import string
import itertools

#########
##Functions for generating vertices' names automatically.
def get_int(used=[]):
    """
    Generator of numbers that are not in 'used'
    """
    a=0
    while True:
        if a not in used:
            yield a
        a=a+1
        
def get_str(used=[],n=1):
    """
    Generator of strings that are not in 'used'
    """
    for i in itertools.product(string.ascii_lowercase, repeat=n):
        if ''.join(i) not in used:
            yield ''.join(i)
    yield from get_str(used,n+1)



#####Stratifold-graph class
class strat_graph(nx.MultiGraph):
    def __init__(self,black=[],white=[],edges=None):
        """
        Class initializer. May receive no arguments. 
        If edges are given,  all vertices involved must belong
        to black or to white (and to only one).
        Raises exception if results in non-bipartite graph
        """
        super().__init__()
        if not set(black).isdisjoint(set(white)):
            raise Exception('Black and white sets non-disjoint')
        self.add_nodes_from(white,bipartite=0)
        self.add_nodes_from(black,bipartite=1)
        if edges is not None:
            #Check if all vertices involved in edges belong to black or white
            nodes=set([e[0] for e in edges]+[e[1] for e in edges])
            if not nodes<=set(black).union(set(white)):
                raise Exception('Incorrect edge(s)')
            #Check if all edges involve one white vertex and one black vertex
            for e in edges:
                if self.nodes()[e[0]]['bipartite']+self.nodes()[e[1]]['bipartite']!=1:
                    raise Exception('Incorrect edge(s)')
            self.add_weighted_edges_from([e for e in edges if len(e)==3])
            self.add_edges_from([e for e in edges if len(e)==2],weight=1)
            
    
    def addEdg(self,edges):
        """
        Adds edges to self. Receives 'edges', a list of tuples,
        where each tuple must have the format
        (white vertex, black vertex, weight)
        or
        (white vertex, black vertex).
        If the last one is given, 'weight' defaults to 1.
        Raises an exception if results in a non-bipartite graph.
        """
        w=[e[0] for e in edges]
        b=[e[1] for e in edges]
        if not set(b).isdisjoint(set(w)):
            raise Exception('Black and white sets non-disjoint')
        if not self.black().isdisjoint(set(w)) or not self.white().isdisjoint(set(b)):
            raise Exception('Incorrect edge')
        self.add_nodes_from(w,bipartite=0)
        self.add_nodes_from(b,bipartite=1)
        self.add_weighted_edges_from([e for e in edges if len(e)==3])
        self.add_edges_from([e for e in edges if len(e)==2],weight=1)
    
    def addNod(self, black=[], white=[]):
        """
        Adds vertices to self.
        Raises exception if results in non-bipartite graph.
        """
        if not set(black).isdisjoint(set(white)):
            raise Exception('Black and white sets non-disjoint')
        if not self.black().isdisjoint(set(white)) or not self.white().isdisjoint(set(black)):
            raise Exception('Incorrect set(s)')
        self.add_nodes_from(white,bipartite=0)
        self.add_nodes_from(black,bipartite=1)
        
    def black_vals(self):
        """
        Returns dictionary where keys are black vertices and
        values are the sum of the weights of their edges
        """
        return dict(self.degree(self.black(),weight='weight'))
    
    def is_trivalent(self):
        """
        Returns true if is a trivalent graph
        """
        return all([x[1]==3 for x in self.degree(self.black(), weight='weight')])
    
    def white(self):
        """
        Returns set of white vertices
        """
        return set([n for n, d in self.nodes(data=True) if d['bipartite']==0])
    
    def black(self):
        """
        Returns set of black vertices
        """
        return set([n for n, d in self.nodes(data=True) if d['bipartite']==1])
        
    def copy(self):
        """
        Returns a copy of self
        """
        edges=[list(e).copy() for e in self.edges(data='weight')]
        H=strat_graph(black=self.black(),
                      white=self.white(),
                      edges=edges)
        return H
    
    def is_horned_tree(self):
        """
        Returns True if self is a horned tree; otherwise, returns False
        """
        #Check if is tree
        if not nx.is_tree(self):
            return False
        #Check if is trivalent
        if not self.is_trivalent():
            return False
        #Check if terminal vertices are white
        leaves=[l for (l,d) in  nx.degree(self) if d==1]
        if not all([self.nodes()[L]['bipartite']==0 for L in leaves]):
            return False
        
        #Black vertices adjacent to terminal vertices should have degree 2
        #else, degree 3
        #there must be at least one black vertex with degree 3
        
        #b1 is set of black vertices adjacent to terminal vertices,
        #which now we know are all white
        b1=set([b for l in leaves for b in self[l]])
        #b2 are the other black vertices
        b2=self.black().difference(b1)
        #Check condition on degrees
        check_b1=all([nx.degree(self)[b]==2 for b in b1])
        check_b2=all([nx.degree(self)[b]==3 for b in b2])
        #Check if there is at least one black vertex with degree 3
        check_3= set()<b2
        if not (check_b1 and check_b2 and check_3):
            return False
        
        #Every non-terminal white vertex has degree 2
        nt_white=self.white().difference(set(leaves))
        if not all([nx.degree(self)[w]==2 for w in nt_white]):
            return False
        #Every terminal edge has label 2
        #Nonterminal edges have label 1
        term_edg_nodes=set(leaves).union(set([b for l in leaves for b in self[l]]))
        not_term_edg_nodes=(set(self.nodes())).difference(term_edg_nodes)
        term_edg=self.edges(nbunch=leaves,data='weight')
        not_term_edg=self.edges(nbunch=not_term_edg_nodes,data='weight')
        check_termW=all([e[2]==2 for e in term_edg])
        check_not_termW=all([e[2]==1 for e in not_term_edg])
        if not(check_termW and check_not_termW):
            return False
        return True
        
    def is_21_collapsible(self):
        """
        Returns None if self is not a 2,1-collapsible tree.
        Returns the root if it is.
        """
        #Check if is tree
        if not nx.is_tree(self):
            return None
        #Check if is trivalent
        if not self.is_trivalent():
            return None
        #All terminal vertices must be white
        leaves=[l for (l,d) in  nx.degree(self) if d==1]
        if not all([self.nodes()[L]['bipartite']==0 for L in leaves]):
            return None
        #If it is a 2,1-collapsible tree, root is unique
        #Will now search for that root.
        for root in self.white():
            #list of simple paths of possible root to terminal nodes
            #As it has been verified that self is a tree,
            #every such path is unique
            paths=[]
            for L in leaves:
                paths=paths+list(nx.all_simple_paths(self,root,L))
            #For every path we must check that edges have alternating labels,
            #starting from 2
            #Flag will indicate wether r has been rejected as a possible root
            flag=False
            for p in paths:
                for i in range(len(p)-2):
                    if (self[p[i]][p[i+1]][0]['weight']%2)!=(i%2):
                        flag=True
                        break
                if flag:
                    break
            #If flag is still False, r is the root
            if not flag:
                return root
        return None
    
    def subg(self,nodes):
        """
        Returns the subgraph of self with given vertices
        """
        B=[b for b in nodes if b in self.black()]
        W=[w for w in nodes if w in self.white()]
        edges=list(self.subgraph(nodes).edges(data='weight'))
        H=strat_graph(black=B,white=W,edges=edges)
        return H
        
    
    def St_B(self):
        """
        Returns list of components of St(B), the closed star 
        of the set of black vertices with degree 3
        """
        B=set([b for b in self.black() if self.degree(b)==3])
        W=set([w for b in B for w in self[b]])
        G=self.subgraph(B.union(W))
        comp=nx.connected_components(G)
        ans=[]
        for C in comp:
            ans.append(self.subg(C))
        return ans
    
    def graph_stB(self):
        """
        Returns a list of the components of G-st(B) (using the
        same notation as in the paper)
        """
        H=self.copy()
        B=set([b for b in self.black() if self.degree(b)==3])
        H.remove_nodes_from(B)
        comp=nx.connected_components(H)
        ans=[]
        for C in comp:
            ans.append(H.subg(C))
        return ans
    
        
    def is_simply_connected(self):
        """
        Implementation of theorem 2. Checks if self is a simply connected
        trivalent 2-stratifold
        """
        #Check if is tree
        if not nx.is_tree(self):
            return False
        #Check if is trivalent
        if not self.is_trivalent():
            return False
        #All terminal vertices must be white
        leaves=[l for (l,d) in  nx.degree(self) if d==1]
        if not all([self.nodes()[L]['bipartite']==0 for L in leaves]):
            return False
        #Components of G-st(B) are 2,1-collapsible trees
        L=self.graph_stB()
        roots=[H.is_21_collapsible() for H in L]
        if not all([r is not None for r in roots]):
            return False
        #Reduced graph contains no horned tree
        STB=self.St_B()
        #Flag will indicate if reduced subgraph has horned subtree
        flag=False
        verts=self.white().union(self.black())
        wv=get_int(used=verts)
        bv=get_str(used=verts)
        for H in STB:
            for w in H.white():
                if w not in roots:
                    bl=next(bv)
                    wh=next(wv)
                    H.addEdg([(w,bl),(wh,bl,2)])
            if H.is_horned_tree():
                flag=True
        if flag:
            return False
        return True
        
        
    def O1(self,white_node,black_nodes1,black_nodes2,W0=None,W1=None,B=None):
        """
        Performs operation O1 on a copy, which is returned.
        -white_node is the node where O1 will take place
        -black_nodes1 and black_nodes2 are the groups of nodes
        that will be separated
        W0 and W1 are the new white vertices created. As white_node will remain
        connected to black_nodes1, W0 will be the white vertex connected
        to black_nodes2. 
        B is the new black vertex created.
        """
        verts=self.white().union(self.black())
        
        if W0 is None or W1 is None:
            W=get_int(used=verts)
            if W0 is None:
                W0=next(W)
            if W1 is None:
                W1=next(W)
        else:
            if W0 in verts or W1 in verts:
                raise Exception('Vertex already in use')
        if B is None:
            B=next(get_str(used=verts))
        else:
            if B in verts:
                raise Exception('Vertex already in use')
                
        
        H=self.copy()
        H.remove_node(white_node)
        edges=[(white_node,b,self[white_node][b][0]['weight']) for b in black_nodes1]
        H.addEdg(edges)
        edges=[(W0,b,self[white_node][b][0]['weight']) for b in black_nodes2]
        H.addEdg(edges)
        H.addEdg([(white_node,B),(W0,B),(W1,B)])
        return H
        
        
    
    def O1_1(self,node,other,node_other,black=None,white=None):
        """
        Performs operation O1* if self and other are disjoints graphs.
        If names for the new white and black vertices are not given, 
        defaults are used
        -other: another strat_graph object
        -node, node_other: white nodes where O1* will be performed
        -black, white: names for new white and black vertices
        Returns a new strat_graph object
        """
        selfverts=self.white().union(self.black())
        otherverts=other.white().union(other.black())
        if not selfverts.isdisjoint(otherverts):
            raise Exception('Graphs not disjoint')
        if node not in self.white() or node_other not in other.white():
            raise Exception('Vertices given are not white')
            
        W=self.white().union(other.white())
        B=self.black().union(other.black())
        edges=[list(e).copy() for e in self.edges(data='weight')]
        edges=edges+[list(e).copy() for e in other.edges(data='weight')]
        H=strat_graph(black=B,white=W,edges=edges)
        
        if black is None:
            black=next(get_str(used=B))
        if white is None:
            white=next(get_int(used=W))
        H.addEdg([(node,black),(node_other,black),(white,black)])
        
        return(H)
        
            
    def O2(self,white_node,new_white=None,new_black=None):
        """
        Performs operation O2 in place
        """
        if new_white is None:
            verts=self.white().union(self.black())
            new_white=next(get_int(verts))
        if new_black is None:
            verts=self.white().union(self.black())
            new_black=next(get_str(verts))
        self.addEdg([(white_node,new_black,2),(new_white,new_black)])
            
       
    def draw(self,trivalent=False):
        """
        Function for drawing the graph.
        Calls the function draw from networkx, coloring black vertices black
        and white vertices gray. 
        If trivalent=True, asserts if graph is trivalent and then draws graph,
        with edges with label 2 bold.
        """
        from matplotlib.pyplot import show
        def num_col(t):
            if t==0:
                return 'gray'
            else:
                return 'black'
        co=[num_col(self.nodes(data='bipartite')[n]) for n in self.nodes()]
        if trivalent==True:
            assert self.is_trivalent()==True
            wi=[e[2]**2 for e in list(self.edges(data='weight'))]
            nx.draw(self,node_color=co,font_color='white',
                    width=wi,with_labels=True)
        else:
            nx.draw(self,node_color=co,font_color='white',
                    with_labels=True)
        show()
        
        
    

def b111(black=None,white=None):
    """
    Returns b111-tree
    -white: list with white vertices
    -black: black vertex (not in iterable)
    If any is not given, default vertices will be used;
    if only one argument is given, it will be ignored to avoid
    repeating names in default and given.
    """
    if black is None or white is None:
        white=[0,1,2]
        black='a'
    G=strat_graph()
    G.addEdg(edges=[(white[0],black),(white[1],black),(white[2],black)])
    return(G)
    
def b12(black=None,white=None):
    """
    Returns b111-tree
    -white: list with white vertices.
    -black: black vertex (not in iterable)
    Edge black-white[0] will have label 1, and
    black-white[1] will have label 2.
    If any is not given, default vertices will be used;
    if only one argument is given, it will be ignored to avoid
    repeating names in default and given.
    """
    if black is None or white is None:
        white=[0,1]
        black='a'
    G=strat_graph()
    G.addEdg(edges=[(white[0],black,1),(white[1],black,2)])
    return(G)