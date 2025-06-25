<p align="center">
  <img src="screenshots/screen4.png" alt="Botanist Logo" width="200" />
</p>

# Botanist 🌱

A command-line time tracker that rewards your focus with a growing ASCII garden.

## What is Botanist?

Botanist gamifies time tracking by growing different flowers based on your session length. The longer you focus, the more beautiful your flower becomes.

## Features

- ⏱️ Track work sessions with `start` and `finish`
- ⏸️ Pause and resume sessions
- 🌼 Earn ASCII flowers based on focus duration
- 📊 Export your data as CSV for analysis
- 🌻 View your garden of completed sessions
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
python botanist.py finish "Completed Python"      # Finish and save
python botanist.py status                         # Check current session
python botanist.py garden                         # View your garden
python botanist.py export                         # Export to CSV
```

## Screenshots


<img src="screenshots/screen1.png" alt="Checking status" width="600">

---

<img src="screenshots/screen2.png" alt="Starting a session" width="600">

---

<img src="screenshots/screen3.png" alt="Your garden grows" width="600">


## Flower Rewards

Your focus duration determines which flower you grow:

< 25 minutes: Seedling
```
  _
 (_)
  |
```

25-45 minutes: Sprout
```
 (@)
  |
```

45-60 minutes: Bud
```
  .-. 
 ( + )
  |*|
```

60+ minutes: Full Bloom
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

## Optional: Obsidian Integration

To save sessions to Obsidian, set the environment variable:

```bash
export BOTANIST_OBSIDIAN_PATH="/path/to/your/obsidian/file.md"
```

Add this to your ~/.zshrc or ~/.bashrc to make it permanent.