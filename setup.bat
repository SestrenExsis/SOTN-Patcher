
python src/sotn_extractor.py "build/Castlevania - Symphony of the Night (Track 1).bin" "build/extraction.json"
python src/sotn_patcher.py "build/patches"
python src/sotn_ppf.py "build/extraction.json" --data="data/" --template="build/vanilla-changes.json"
