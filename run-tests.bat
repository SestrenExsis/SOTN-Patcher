
@REM To recompute hashes, run the following:
@REM sha1sum build/ppf/* > tests/checksums.sha1

set EXTRACT="build/extraction.json"

python src/sotn_extractor.py "build/Castlevania - Symphony of the Night (Track 1).bin" %EXTRACT% || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" || goto :error

python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/assign-power-of-wolf-relic-a-unique-id.json" --ppf="build/ppf/assign-power-of-wolf-relic-a-unique-id.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/clock-hands-mod.json" --ppf="build/ppf/clock-hands-mod.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/customized-castle-map-reveals.json" --ppf="build/ppf/customized-castle-map-reveals.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/customized-color-palettes.json" --ppf="build/ppf/customized-color-palettes.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/customized-enemy-drops.json" --ppf="build/ppf/customized-enemy-drops.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/disable-clipping-on-one-way-walls.json" --ppf="build/ppf/disable-clipping-on-one-way-walls.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/enable-debug-mode.json" --ppf="build/ppf/enable-debug-mode.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/randomized-items.json" --ppf="build/ppf/randomized-items.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/randomized-relics.json" --ppf="build/ppf/randomized-relics.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/sample-randomized-map.json" --ppf="build/ppf/sample-randomized-map.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/shop-relic-name.json" --ppf="build/ppf/shop-relic-name.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/shuffle-spike-room.json" --ppf="build/ppf/shuffle-spike-room.ppf" || goto :error
python src/sotn_patcher.py %EXTRACT% --data="data/" --changes="tests/softlock-in-alchemy-lab-maria-cutscene.json" --ppf="build/ppf/softlock-in-alchemy-lab-maria-cutscene.ppf" || goto :error

sha1sum -c tests/checksums.sha1

goto :EOF

:error
echo Failed with error #%errorlevel%
exit /b %errorlevel%