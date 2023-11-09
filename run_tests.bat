echo off
rem Set TESTING environment variable to true
set TESTING=true

rem Run pytest
pytest

rem Set TESTING environment variable back to false
set TESTING=false