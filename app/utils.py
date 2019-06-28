import pickle
import ast

def save_state(object):
    return str(pickle.dumps(object))

def load_state(state):

    if state is None:
        return {}
    
    try:
        state = ast.literal_eval(state)
        state = pickle.loads(state)
    
    except Exception as e:
        print(f"Error loading state: {e}")
        state = {}
    
    return state