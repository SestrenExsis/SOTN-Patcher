
@REM To recompute hashes, run the following:
@REM sha1sum build/ppf/* > tests/checksums.sha1

python src/sotn_extractor.py "build/Castlevania - Symphony of the Night (Track 1).bin" "build/extraction.json" || goto :error
python src/sotn_patcher.py "build/extraction.json" || goto :error

python src/sotn_patcher.py "build/extraction.json" --data="data/" --changes="tests/clock-hands-mod.json" --ppf="build/ppf/clock-hands-mod.ppf" || goto :error
python src/sotn_patcher.py "build/extraction.json" --data="data/" --changes="tests/disable-clipping-on-screen-edge-of-demon-switch-wall.json" --ppf="build/ppf/disable-clipping-on-screen-edge-of-demon-switch-wall.ppf" || goto :error
python src/sotn_patcher.py "build/extraction.json" --data="data/" --changes="tests/softlock-in-alchemy-lab-maria-cutscene.json" --ppf="build/ppf/softlock-in-alchemy-lab-maria-cutscene.ppf" || goto :error
python src/sotn_patcher.py "build/extraction.json" --data="data/" --changes="tests/customized-castle-map-reveals.json" --ppf="build/ppf/customized-castle-map-reveals.ppf" || goto :error
python src/sotn_patcher.py "build/extraction.json" --data="data/" --changes="tests/sample-randomized-map.json" --ppf="build/ppf/sample-randomized-map.ppf" || goto :error
python src/sotn_patcher.py "build/extraction.json" --data="data/" --changes="tests/randomized-relics.json" --ppf="build/ppf/randomized-relics.ppf" || goto :error

sha1sum -c tests/checksums.sha1

goto :EOF

:error
echo Failed with error #%errorlevel%
exit /b %errorlevel%