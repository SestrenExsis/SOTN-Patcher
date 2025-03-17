
python src/sotn_extractor.py "build/Castlevania - Symphony of the Night (Track 1).bin" "build/extraction.json" || goto :error
python src/sotn_patcher.py "build/extraction.json" --changes="tests/softlock-in-alchemy-lab-maria-cutscene.json" --aliases="data/aliases.yaml" --ppf="build/ppf/softlock-in-alchemy-lab-maria-cutscene.ppf" || goto :error
sha1sum -c tests/softlock-in-alchemy-lab-maria-cutscene.sha1

goto :EOF

:error
echo Failed with error #%errorlevel%
exit /b %errorlevel%