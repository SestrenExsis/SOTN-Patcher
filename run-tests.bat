
@REM To recompute hashes, run the following:
@REM sha1sum build/ppf/* > tests/checksums.sha1

set BUILD="build"

python src/sotn_extractor.py "build/Castlevania - Symphony of the Night (Track 1).bin" "build" || goto :error
python src/sotn_patcher.py %BUILD% || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" || goto :error

python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/sample-entity-layout.json" --ppf="build/ppf/sample-entity-layout.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/assign-power-of-wolf-relic-a-unique-id.json" --ppf="build/ppf/assign-power-of-wolf-relic-a-unique-id.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/clock-hands-mod.json" --ppf="build/ppf/clock-hands-mod.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/customized-castle-map-reveals.json" --ppf="build/ppf/customized-castle-map-reveals.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/customized-color-palettes.json" --ppf="build/ppf/customized-color-palettes.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/customized-enemy-drops.json" --ppf="build/ppf/customized-enemy-drops.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/debug-sound-normalization.json" --ppf="build/ppf/debug-sound-normalization.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/disable-clipping-on-one-way-walls.json" --ppf="build/ppf/disable-clipping-on-one-way-walls.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/enable-debug-mode.json" --ppf="build/ppf/enable-debug-mode.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/fix-confessional-bell-sound.json" --ppf="build/ppf/fix-confessional-bell-sound.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/fix-palette-darkening-in-castle-entrance.json" --ppf="build/ppf/fix-palette-darkening-in-castle-entrance.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/fix-secret-room-map-pixels.json" --ppf="build/ppf/fix-secret-room-map-pixels.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/improve-normalized-room-visuals.json" --ppf="build/ppf/improve-normalized-room-visuals.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/mix-items-and-relics.json" --ppf="build/ppf/mix-items-and-relics.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/move-drawbridge-room-vertically.json" --ppf="build/ppf/move-drawbridge-room-vertically.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/normalize-ferryman-gate.json" --ppf="build/ppf/normalize-ferryman-gate.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/normalize-room-connections.json" --ppf="build/ppf/normalize-room-connections.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/normalize-particle-effects.json" --ppf="build/ppf/normalize-particle-effects.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/preserve-map-exploration.json" --ppf="build/ppf/preserve-map-exploration.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/preserve-map-revelation.json" --ppf="build/ppf/preserve-map-revelation.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/prevent-death-meeting-softlocks.json" --ppf="build/ppf/prevent-death-meeting-softlocks.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/prevent-softlocks-after-defeating-scylla.json" --ppf="build/ppf/prevent-softlocks-after-defeating-scylla.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/prevent-softlocks-at-demon-switch-wall.json" --ppf="build/ppf/prevent-softlocks-at-demon-switch-wall.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/prevent-softlocks-at-left-gear-room-wall.json" --ppf="build/ppf/prevent-softlocks-at-left-gear-room-wall.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/prevent-softlocks-at-pendulum-room-wall.json" --ppf="build/ppf/prevent-softlocks-at-pendulum-room-wall.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/prevent-softlocks-at-plaque-room-wall.json" --ppf="build/ppf/prevent-softlocks-at-plaque-room-wall.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/prevent-softlocks-at-snake-column-wall.json" --ppf="build/ppf/prevent-softlocks-at-snake-column-wall.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/prevent-softlocks-at-tall-zig-zag-room-wall.json" --ppf="build/ppf/prevent-softlocks-at-tall-zig-zag-room-wall.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/randomized-items.json" --ppf="build/ppf/randomized-items.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/randomized-relics.json" --ppf="build/ppf/randomized-relics.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/sample-randomized-map.json" --ppf="build/ppf/sample-randomized-map.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/shop-relic-name.json" --ppf="build/ppf/shop-relic-name.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/shuffle-spike-room.json" --ppf="build/ppf/shuffle-spike-room.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/shuffle-starting-gear.json" --ppf="build/ppf/shuffle-starting-gear.ppf" || goto :error
python src/sotn_ppf.py %BUILD% --data="data/" --changes="tests/skip-maria-cutscene-in-alchemy-laboratory.json" --ppf="build/ppf/skip-maria-cutscene-in-alchemy-laboratory.ppf" || goto :error

sha1sum -c tests/checksums.sha1

goto :EOF

:error
echo Failed with error #%errorlevel%
exit /b %errorlevel%