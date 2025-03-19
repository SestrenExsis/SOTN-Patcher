
python src/sotn_extractor.py "build/Castlevania - Symphony of the Night (Track 1).bin" "build/extraction.json" || goto :error
python src/sotn_patcher.py "build/extraction.json" --changes="tests/softlock-in-alchemy-lab-maria-cutscene.json" --aliases="data/aliases.yaml" --ppf="build/ppf/softlock-in-alchemy-lab-maria-cutscene.ppf" || goto :error
python src/sotn_patcher.py "build/extraction.json" --changes="tests/customized-castle-map-reveals.json" --aliases="data/aliases.yaml" --ppf="build/ppf/customized-castle-map-reveals.ppf" || goto :error
python src/sotn_patcher.py "build/extraction.json" --changes="tests/sample-randomized-map.json" --aliases="data/aliases.yaml" --ppf="build/ppf/sample-randomized-map.ppf" || goto :error

sha1sum -c tests/checksums.sha1

goto :EOF

:error
echo Failed with error #%errorlevel%
exit /b %errorlevel%