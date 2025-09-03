"""
Flower definitions and assignment logic for Botanist.
"""

import random

# Original flowers (keeping these as they are)
SEEDLING = """_
(_)
 |"""

BUD = """(@)
 | """

BLOOM = """ .-. 
( + )
 |*|  """

FULL_BLOOM = """        
        #%:.     
 #%=   ###%=:    
##%=   |##%=:    
##%=   ###%=:    
 #%%=  |##%=:    
 ##%== ###%=:    ===
  ##%%=!##%=:    ====
   ###%%##%=   :==== 
    ######%=: .:==== 
      ####%%======= 
       ###%%%===: 
       |%#%%=:=:  
       ####%=:   
       |##%%:    
-------####%:---=
       |%#%%:    """

# New Eastern-themed symmetric flowers

LOTUS_SMALL = """   .-.   
  ( * )  
   '-'   
    |    """

LOTUS_MEDIUM = """  .--.  
 ( ** ) 
( **** )
 '--'   
   ||   """

LOTUS_LARGE = """   .---.   
  ( *** )  
 ( ***** ) 
( ******* )
  '---'    
    |||    """

CHRYSANTHEMUM = """   ___   
  (o*o)  
 (*o*o*) 
  (o*o)  
   |||   """

PLUM_BLOSSOM = """  .*.  
 *.*.* 
*.*.*.*
 *.*.* 
  .*. 
   |   """

CHERRY_BLOSSOM = """   oOo   
  oOOOo  
 oOOOOOo 
  oOOOo  
   oOo   
    |    """

ORCHID = """  \\ | /  
 - *** - 
  / | \\  
    |    """

PEONY = """  (@@@)  
 (@@@@@) 
(@@@@@@@)
 (@@@@@) 
  (@@@)  
    |    """

BAMBOO_FLOWER = """   |||   
  |*|*|  
 |*|*|*| 
  |*|*|  
   |||   
    |    """

# Special 2+ hour flower
QUEEN_OF_THE_NIGHT = """     .***.     
   .*******.   
  ***********  
 *************
***************
 ************* 
  ***********  
   *******.   
     .***.     
       |       
       |       
 ═══════════════
 Queen of the Night
 ═══════════════"""


def assign_flower(duration, streak=0):
    """Assign flower based on duration with Eastern theme"""
    minutes = duration / 60
    
    # Keep original progression for short sessions
    if minutes < 25:
        return SEEDLING
    elif minutes < 45:
        return BUD
    elif minutes < 60:
        return BLOOM
    elif minutes < 120:
        # For 60-120 minutes, randomly choose from Eastern flowers
        eastern_flowers = [
            LOTUS_SMALL,
            LOTUS_MEDIUM,
            LOTUS_LARGE,
            CHRYSANTHEMUM,
            PLUM_BLOSSOM,
            CHERRY_BLOSSOM,
            ORCHID,
            PEONY,
            BAMBOO_FLOWER,
            FULL_BLOOM  # Include original as one option
        ]
        return random.choice(eastern_flowers)
    else:
        # 2+ hours gets Queen of the Night
        return QUEEN_OF_THE_NIGHT


def assign_flower_weighted(duration, session_number=0):
    """Assign flower with weighted random selection"""
    minutes = duration / 60
    
    if minutes < 25:
        return SEEDLING
    elif minutes < 45:
        return BUD
    elif minutes < 60:
        return BLOOM
    elif minutes < 90:
        # 60-90 minutes: smaller Eastern flowers
        flowers = [LOTUS_SMALL, ORCHID, PLUM_BLOSSOM, CHERRY_BLOSSOM]
        # Use session number for variety but still some randomness
        index = (session_number + random.randint(0, 1)) % len(flowers)
        return flowers[index]
    elif minutes < 120:
        # 90-120 minutes: larger Eastern flowers
        flowers = [LOTUS_LARGE, CHRYSANTHEMUM, PEONY, BAMBOO_FLOWER, FULL_BLOOM]
        index = (session_number + random.randint(0, 1)) % len(flowers)
        return flowers[index]
    else:
        # 2+ hours: Queen of the Night
        return QUEEN_OF_THE_NIGHT