
python src/sotn_extractor.py "build/Castlevania - Symphony of the Night (Track 1).bin" "build/extraction.json"
python src/sotn_data.py "build/extraction.json" "build/core-data.json"
python src/sotn_patcher.py "build/core-data.json"
