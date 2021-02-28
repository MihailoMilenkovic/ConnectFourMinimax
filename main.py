def my_agent(observation, configuration):
    def get_all_windows(board,configuration):
        windows=[]
        #horizontal windows
        for i in range(configuration.rows):
            for j in range(configuration.columns-configuration.inarow+1):
                new_window=[]
                for k in range(configuration.inarow):
                    new_window.append((i,j+k))
                windows.append(new_window)
        #vertical windows
        for i in range(configuration.rows-configuration.inarow+1):
            for j in range(configuration.columns):
                new_window=[]
                for k in range(configuration.inarow):
                    new_window.append((i+k,j))
                windows.append(new_window)
        #diagonal windows
        for i in range(configuration.rows-configuration.inarow+1):
            for j in range(configuration.columns-configuration.inarow+1):
                new_window=[]
                for k in range(configuration.inarow):
                    new_window.append((i+k,j+k))
                #print(new_window)
                windows.append(new_window)
                new_window=[]
                for k in range(configuration.inarow):
                    new_window.append((i+k,j+configuration.inarow-k-1))
                windows.append(new_window)
                #print(new_window)
        return windows
    
    def get_heuristic_eval(board,windows,mark,next_to_move):
        ev=0
        available=[]
        for j in range(len(board[0])):
            for h in range(len(board)):
                if board[h][j]==0 and (h==len(board)-1  or board[h+1][j]!=0):
                    available.append((h,j))
        #print(available)
        for window in windows:
            window_eval=0
            our_cnt,other_cnt,avails=(0,0,0,0)
            for (x,y) in window:
                if (x,y) in available:
                    avails+=1
                if board[x][y]==mark:
                    our_cnt+=1
                elif board[x][y]==mark%2+1:
                    other_cnt+=1
            if other_cnt>0 and our_cnt>0:
                continue
            ourCoef,otherCoef=(1,1)
            if mark==next_to_move:
                ourCoef=25
            else:
                otherCoef=25
            
            if other_cnt==4:
                window_eval=-10000000000000
            elif (other_cnt==3 and avails==1):
                window_eval=-1000000*otherCoef/ourCoef
            elif other_cnt==3:
                window_eval=-200*otherCoef/ourCoef
            elif other_cnt==2:
                window_eval=-1
            elif our_cnt==4:
                window_eval=10000000000000
            elif (our_cnt==3 and avails==1):
                window_eval=1000000*ourCoef/otherCoef
            elif our_cnt==3:
                window_eval=200*ourCoef/otherCoef
            elif our_cnt==2:
                window_eval=1
            ev+=window_eval
        return ev

    def drop_piece(board,col,mark,configuration):
        next_board=board.copy()
        for row in range(configuration.rows-1,-1,-1):
            if next_board[row][col]==0:
                break
        next_board[row][col]=mark
        return next_board
    
    def game_finished(board,windows,mark):
        available=[]
        for j in range(len(board[0])):
            for h in range(len(board)):
                if board[h][j]==0 and (h==len(board)-1  or board[h+1][j]!=0):
                    available.append((h,j))
        if(len(available)==0):
            return True
        for window in windows:
            our_cnt,other_cnt=(0,0)
            for (x,y) in window:
                if board[x][y]==mark:
                    our_cnt+=1
                elif board[x][y]==mark%2+1:
                    other_cnt+=1
            if(our_cnt==len(windows[0]) or other_cnt==len(windows[0])):
                return True
        return False
    
    def get_minimax_eval(board,configuration,windows,depth,mark,next_to_move,alpha=-10**50,beta=10**50):
        if(depth==0):
            return get_heuristic_eval(board,windows,mark,next_to_move)
        if(game_finished(board,windows,mark)):
            return get_heuristic_eval(board,windows,mark,next_to_move)
        ev={}
        heur={}
        for c in range(configuration.columns):
            if board[0][c]==0:
                next_board=drop_piece(board,c,next_to_move,configuration)
                heur[c]=get_heuristic_eval(next_board,windows,mark,next_to_move%2+1)
        orderedItems=sorted(heur,key=heur.get,reverse=mark==next_to_move)
        #print(orderedItems)
        #ev={}
        #for c in range(configuration.columns):
        for c in orderedItems:
            if board[0][c]==0:
                next_board=drop_piece(board,c,next_to_move,configuration)
                ev[c]=get_minimax_eval(next_board,configuration,windows,depth-1,mark,next_to_move%2+1,alpha,beta) 
                if next_to_move==mark:
                    alpha=max(alpha,ev[c])
                else:
                    beta=min(beta,ev[c])
                if alpha>=beta:
                    break
                #if(depth==2):
                #    print("(depth "+str(depth)+") eval for c:",c,":",ev[c])
        if next_to_move!=mark:
            return min(ev.values())
        else:
            return max(ev.values())
        
    
    from random import choice
    import numpy as np
    board=np.asarray(observation.board).reshape(configuration.rows,configuration.columns)
    windows=get_all_windows(board,configuration)
    #ev=get_heuristic_eval(board,windows,observation.mark,observation.mark)
    ev={}
    for c in range(configuration.columns):
        if board[0][c]==0:
            next_board=drop_piece(board,c,observation.mark,configuration)
            #ev[c]=get_heuristic_eval(next_board,windows,observation.mark,observation.mark%2+1)
            #print("getting eval for:",c)
            ev[c]=get_minimax_eval(next_board,configuration,windows,4,observation.mark,observation.mark%2+1)
            #print("eval is:",ev[c])
            #print(c,"ev:",ev[c])
    maxes=[c for c in ev.keys() if ev[c]==max(ev.values())]
    return maxes[0]
