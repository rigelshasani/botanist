<p align="center">
  <img src="screenshots/screen4.png" alt="Botanist Logo" 
  width="200" />
</p>

# Botanist 🌱

A command-line time tracker that rewards your focus with a growing ASCII garden.

## What is Botanist?

Botanist gamifies time tracking by growing different flowers based on your session length. The longer you focus, the more beautiful your flower becomes. Bonus: sessions now support advanced analytics and rich integration with journaling tools like Obsidian.

## Features

- ⏱️ Track work sessions with `start`, `pause`, `resume`, and `finish`
- 🌼 Earn ASCII flowers based on focus duration
- 🐛 Avoid duplicates via session collision checks
- 🔍 Preview sessions before saving (dry run mode)
- 📈 View weekly stats with `analyze`
- 🪄 Merge sessions manually from `.csv` or `.json` with `merge_manual.py`
- 📊 Export your data to CSV for custom analysis
- 🌻 View your complete garden of completed sessions
- 📝 Optional Obsidian integration

## Installation

```bash
git clone https://github.com/rigelshasani/botanist.git
cd botanist
```

## Usage

```bash
python botanist.py start                          # Start tracking
python botanist.py pause                          # Take a break
python botanist.py resume                         # Resume working
python botanist.py finish "Finished Python Drill" # Finish and save
python botanist.py status                         # Check current session
python botanist.py garden                         # View your garden
python botanist.py export                         # Export to CSV
python botanist.py weekly                        # Weekly report 
```

## Screenshots


<img src="screenshots/screen1.png" alt="Checking status" width="600">

---

<img src="screenshots/screen2.png" alt="Starting a session" width="600">

---

<img src="screenshots/screen3.png" alt="Your garden grows" width="600">

---

<img src="screenshots/screen5.png" alt="Weekly Analysis" width="400">

---


## 🌼 Flower Rewards

Each completed session plants a flower in your ASCII garden. The longer you focus, the more elaborate your flower can become.

However, there's also a touch of randomness—to keep your garden visually diverse and surprising. Even short sessions might bloom beautifully now and then, while long ones may grow humbler flowers, depending on the mood of the soil 🌱.

### Examples of Possible Flowers

**Seedling** (often < 25 minutes)
```
  _
 (_)
  |
```

**Sprout**
```
 (@)
  |
```

**Bud**
```
 .-. 
( + )
 |*|
```

**Full Bloom**
```
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
       |%#%%:    
```

**Specialty: Queen of the Night** (rare, for legendary focus)
```
     .***.     
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
═════════════════════
 Queen of the Night  
═════════════════════
```

These flowers are selected based on your session duration, but the garden rewards you with surprises—symbolizing that every session counts, and not every bloom looks the same.

## Optional: Obsidian Integration

To automatically append finished session logs to your Obsidian notes:

```bash
export BOTANIST_OBSIDIAN_PATH="/path/to/your/obsidian/file.md"
```

Add this line to your `~/.zshrc`, `~/.bashrc`, or `~/.profile` to persist the setting.

## Data Format

All sessions are stored in `.hiddenGarden.json` with the following structure:

```json
{
  "date": "2025-07-18",
  "start_time": "2025-07-18 10:22:12",
  "end_time": "2025-07-18 12:28:28",
  "duration": 7576.38,
  "description": "None provided.",
  "flower": "(ASCII flower or Unicode)"
}
```

## Weekly Analysis Output Example

```
Week 4:  16.37 h
  Friday     (Jul 11)   2.57 h  █████
  Saturday   (Jul 12)   1.87 h  ███
  Sunday     (Jul 13)   2.63 h  █████
  ...
Total hours across all weeks: 45.12 h
```

## Coming Soon

- 📅 Monthly garden summary
- 🔔 Notification system for session intervals
- 📤 Cloud sync

---

Botanist was built to make your work bloom. Focus hard, and let your flowers speak for your dedication.