
python src/sotn_extractor.py "build/Castlevania - Symphony of the Night (Track 1).bin" "build"
python src/sotn_patcher.py "build"
python src/sotn_ppf.py "build" --data="data"
