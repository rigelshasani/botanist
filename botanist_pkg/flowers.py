"""
Flower definitions and assignment logic for Botanist.
"""

import random
from .config import get_time_thresholds

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

# Advanced artistic flowers (60-90 minutes)
MANDALA_FLOWER = """    .--*--.    
  .*'     '*.  
 *'  .---.  '*
*   ( *** )   *
|    '***'    |
*   ( *** )   *
 *. '-----' .*
  '*.     .*'  
    '--*--'    
       |       """

CRYSTAL_BLOOM = """   /\\/\\/\\   
  < **** >  
 /  ****  \\ 
<  *.**.* >
 \\ **** / 
  < **** >  
   \\/\\/\\/   
     ||     """

GEOMETRIC_ROSE = """   ___   
  /***\\  
 <*****> 
  \\***/  
   |*|   
  /*\\   
 <***>  
  \\*/   
   |    """

STARBURST = """   \\  |  /   
  \\ \\|/ /   
---\\**/---  
   /*\\    
  / | \\   
    |     """

# Rare flowers (90-120 minutes)  
PHOENIX_FEATHER = """    *^*^*    
   ^*^*^*^   
  *^*^*^*^*  
 ^*^*^^^*^*^ 
*^*^*^*^*^*^*
 ^*^*^^^*^*^ 
  *^*^*^*^*  
   ^*^*^*^   
    *^*^*    
      |      
    ----- """

DRAGON_SCALE = """  ≋≋≋≋≋≋≋  
 ≋≋≋≋≋≋≋≋≋ 
≋≋≋≋≋≋≋≋≋≋≋
≋≋≋ ≋≋≋ ≋≋≋
≋≋≋≋≋≋≋≋≋≋≋
 ≋≋≋≋≋≋≋≋≋ 
  ≋≋≋≋≋≋≋  
     |     
   -----   """

CELESTIAL_LOTUS = """     ☾ ☽     
   ☽ ◊ ◊ ☾   
  ◊ ◊ ◊ ◊ ◊  
 ☾ ◊ ◊◊◊ ◊ ☽ 
☽ ◊ ◊◊◊◊◊ ◊ ☾
 ☾ ◊ ◊◊◊ ◊ ☽ 
  ◊ ◊ ◊ ◊ ◊  
   ☽ ◊ ◊ ☾   
     ☾ ☽     
       |     
     ===== """

INFINITY_BLOOM = """   ∞   ∞   
  ∞ ◈ ◈ ∞  
 ∞ ◈ ◈ ◈ ◈ ∞
∞ ◈ ◈ ◈ ◈ ◈ ∞
 ∞ ◈ ◈ ◈ ◈ ∞
  ∞ ◈ ◈ ∞  
   ∞   ∞   
     |     
   -----   """

# Legendary flowers (120+ minutes)
WORLD_TREE = """           *           
      *   ***   *      
   *  **  ***  **  *   
 *** *** ***** *** *** 
***** ************* ****
 *** *** ***** *** *** 
   *  **  ***  **  *   
      *   ***   *      
           ***          
           |||          
        ========        
     WORLD TREE     
        ========        """

COSMIC_FLOWER = """       ✦ ★ ✦       
    ★ ✧ ★ ★ ✧ ★    
  ✦ ★ ✧ ★ ★ ✧ ★ ✦  
 ★ ✧ ★ ★ ★ ★ ★ ✧ ★ 
✦ ★ ★ ★ ★★★ ★ ★ ★ ✦
 ★ ✧ ★ ★ ★ ★ ★ ✧ ★ 
  ✦ ★ ✧ ★ ★ ✧ ★ ✦  
    ★ ✧ ★ ★ ✧ ★    
       ✦ ★ ✦       
         |||         
    ===============  
     COSMIC BLOOM    
    ===============  """

ETERNAL_FLAME = """      △ △ △      
    △ ▲ ▲ ▲ △    
  △ ▲ ▲ ▲ ▲ ▲ △  
 ▲ ▲ ▲ ▲▲▲ ▲ ▲ ▲ 
△ ▲ ▲ ▲▲▲▲▲ ▲ ▲ △
 ▲ ▲ ▲ ▲▲▲ ▲ ▲ ▲ 
  △ ▲ ▲ ▲ ▲ ▲ △  
    △ ▲ ▲ ▲ △    
      △ △ △      
        |||        
   =============   
   ETERNAL FLAME   
   =============   """

# Ultimate legendary flower (3+ hours)
UNIVERSE_GARDEN = """           ✧ ★ ✦ ★ ✧           
      ★ ✦ ✧ ◊ ◊ ◊ ✧ ✦ ★      
   ✦ ◊ ◊ ◊ ◊ ◊ ◊ ◊ ◊ ◊ ✦   
 ★ ◊ ◊ ◊ ◊ ◊◊◊ ◊ ◊ ◊ ◊ ★ 
✧ ◊ ◊ ◊ ◊ ◊◊◊◊◊ ◊ ◊ ◊ ◊ ✧
◊ ◊ ◊ ◊ ◊ ◊◊◊◊◊ ◊ ◊ ◊ ◊ ◊
★ ◊ ◊ ◊ ◊◊◊***◊◊◊ ◊ ◊ ◊ ★
◊ ◊ ◊ ◊ ◊ ◊◊◊◊◊ ◊ ◊ ◊ ◊ ◊
✧ ◊ ◊ ◊ ◊ ◊◊◊◊◊ ◊ ◊ ◊ ◊ ✧
 ★ ◊ ◊ ◊ ◊ ◊◊◊ ◊ ◊ ◊ ◊ ★ 
   ✦ ◊ ◊ ◊ ◊ ◊ ◊ ◊ ◊ ◊ ✦   
      ★ ✦ ✧ ◊ ◊ ◊ ✧ ✦ ★      
           ✧ ★ ✦ ★ ✧           
              |||              
     =======================   
        UNIVERSE GARDEN        
     =======================   """

# Special 2+ hour flower (keeping original)
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
    """
    Assign flower based on session duration with artistic progression.
    Longer sessions earn more elaborate and rare flowers.
    
    Args:
        duration (float): Session duration in seconds
        streak (int): Current streak (for future use)
        
    Returns:
        str: ASCII art flower appropriate for the session duration
    """
    thresholds = get_time_thresholds()
    minutes = duration / 60
    
    # Basic flowers (short sessions)
    if duration < thresholds["seedling"]:  # < 25 min
        return SEEDLING
    elif duration < thresholds["bud"]:     # 25-45 min
        return BUD
    elif duration < thresholds["bloom"]:   # 45-60 min
        return BLOOM
    
    # Medium sessions (60-90 min) - Traditional Eastern flowers
    elif minutes < 90:
        eastern_flowers = [
            LOTUS_SMALL,
            LOTUS_MEDIUM, 
            CHRYSANTHEMUM,
            PLUM_BLOSSOM,
            CHERRY_BLOSSOM,
            ORCHID,
            PEONY,
            BAMBOO_FLOWER
        ]
        return random.choice(eastern_flowers)
    
    # Advanced sessions (90-120 min) - Artistic and geometric flowers  
    elif duration < thresholds["queen"]:   # 90-120 min
        advanced_flowers = [
            LOTUS_LARGE,
            MANDALA_FLOWER,
            CRYSTAL_BLOOM, 
            GEOMETRIC_ROSE,
            STARBURST,
            FULL_BLOOM
        ]
        return random.choice(advanced_flowers)
    
    # Long sessions (120-150 min) - Rare mystical flowers
    elif minutes < 150:
        rare_flowers = [
            PHOENIX_FEATHER,
            DRAGON_SCALE,
            CELESTIAL_LOTUS,
            INFINITY_BLOOM,
            QUEEN_OF_THE_NIGHT
        ]
        return random.choice(rare_flowers)
    
    # Very long sessions (150-180 min) - Legendary flowers
    elif minutes < 180:
        legendary_flowers = [
            WORLD_TREE,
            COSMIC_FLOWER,
            ETERNAL_FLAME
        ]
        return random.choice(legendary_flowers)
    
    # Ultimate sessions (180+ min / 3+ hours) - Universe Garden
    else:
        return UNIVERSE_GARDEN


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