@echo off
setlocal EnableExtensions

REM ============================================================================
REM  Deploy the ELOBS Pre-Define Viewer into a local OpenStudyBuilder checkout
REM  and rebuild/restart the affected Docker containers.
REM
REM  - API extension  : Python package -> underscore folder name
REM  - GUI extension  : StudyBuilder convention -> kebab-case folder name
REM
REM  Targets are deleted first, then freshly copied (clean deploy).
REM ============================================================================

REM ---- Source folders (this repo) -------------------------------------------
set "SRC_API=C:\git\elobs-pre-define-display\osb-api-extension\elobs_pre_define_display"
set "SRC_GUI=C:\git\elobs-pre-define-display\osb-frontend-extension\elobs-pre-define-display"

REM ---- OpenStudyBuilder checkout (adjust OSB_ROOT if yours differs) ----------
set "OSB_ROOT=C:\git\osb-public-NN"
set "DST_API=%OSB_ROOT%\api\extensions\elobs_pre_define_display"
set "DST_GUI=%OSB_ROOT%\frontend\src\extensions\elobs-pre-define-display"

echo.
echo === ELOBS Pre-Define Viewer: deploy to OpenStudyBuilder ===

REM ---- Sanity checks --------------------------------------------------------
if not exist "%SRC_API%\" (
  echo ERROR: API source not found: %SRC_API%
  exit /b 1
)
if not exist "%SRC_GUI%\" (
  echo ERROR: GUI source not found: %SRC_GUI%
  exit /b 1
)
if not exist "%OSB_ROOT%\" (
  echo ERROR: OpenStudyBuilder root not found: %OSB_ROOT%
  exit /b 1
)

REM ---- [1/4] API extension --------------------------------------------------
echo.
echo [1/4] Copying API extension...
if exist "%DST_API%\" (
  echo   Removing existing %DST_API%
  rmdir /s /q "%DST_API%"
)
xcopy "%SRC_API%" "%DST_API%\" /E /I /Y /Q >nul
if errorlevel 1 ( echo ERROR: API copy failed & exit /b 1 )
echo   Copied to %DST_API%

REM ---- [2/4] GUI extension --------------------------------------------------
echo.
echo [2/4] Copying frontend extension...
if exist "%DST_GUI%\" (
  echo   Removing existing %DST_GUI%
  rmdir /s /q "%DST_GUI%"
)
xcopy "%SRC_GUI%" "%DST_GUI%\" /E /I /Y /Q >nul
if errorlevel 1 ( echo ERROR: GUI copy failed & exit /b 1 )
echo   Copied to %DST_GUI%

REM ---- [3/4] Rebuild extensions API container -------------------------------
echo.
echo [3/4] Rebuilding extensionsapi container...
pushd "%OSB_ROOT%"
docker compose up -d --build --force-recreate --no-deps extensionsapi
if errorlevel 1 ( echo ERROR: extensionsapi rebuild failed & popd & exit /b 1 )

REM ---- [4/4] Rebuild frontend container -------------------------------------
echo.
echo [4/4] Rebuilding frontend container...
docker compose up -d --build --force-recreate --no-deps frontend
if errorlevel 1 ( echo ERROR: frontend rebuild failed & popd & exit /b 1 )
popd

echo.
echo === Done. ===
echo   Frontend : http://localhost:5005/studies/elobs-pre-define-display
echo   API docs : http://localhost:5005/extensions-api/docs#/ElobsPreDefineDisplay
echo.

endlocal
