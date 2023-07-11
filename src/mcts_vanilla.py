
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.


def uct(child, parent, identity):

    if identity == 'red':
        winrate = child.wins / child.visits
    else:
        winrate = 1 - child.wins / child.visits
    return winrate + explore_faction*sqrt(log(parent.visits)/child.visits)

# red = you ; blue = other player
def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    if identity == 'red':
        other_id = 'blue'
    else:
        other_id = 'red'

    if node.untried_actions or board.is_ended(state):
        return node, state
    else:
        max = -1
        best_child = None
        for child in node.child_nodes.keys():
            child_uct = uct(child, node, identity)
            if child_uct > max:
                max = child_uct
                best_child = child
        return traverse_nodes(best_child, board, board.next_state(state, node.child_nodes[best_child]), other_id)
            
    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    action = choice(node.untried_actions)
    child_state = board.next_state(state, action)
    child = MCTSNode(node, action, board.legal_actions(child_state))
    node.child_nodes[child] = action
    node.untried_actions.remove(action)
    return child, child_state
    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    if board.is_ended(state):
        return state
    else:
        moves = board.legal_actions(state)
        action = choice(moves)
        return rollout(board, board.next_state(state, action))
        

        
def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    node.wins = node.wins + won
    node.visits = node.visits + 1
    if node.parent is None:
        return
    else:
        backpropagate(node.parent, won)
        


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    # which player is this bot playing 
    identity_of_bot = board.current_player(state)
    # create a mct from the state of the game with all untried actions
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    # i guess we create an entire mcts tree every think call with a limited number of nodes (simulations)
    # repeatedly expand / simulate mcts
    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        leaf, leaf_state = traverse_nodes(node, board, sampled_game, 'red')

        if not leaf.untried_actions:
            break

        child, child_state = expand_leaf(leaf, board, leaf_state)
        end_state = rollout(board, child_state)
        won = (board.points_values(end_state))[identity_of_bot]
        won = 1 if won==1 else 0
        backpropagate(child, won)

    best_wr = -1
    for child in root_node.child_nodes.keys():
        if child.wins / child.visits > best_wr:
            best_wr = child.wins / child.visits
            best_child = child
    return best_child.parent_action
    
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
