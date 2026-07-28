export PYTHONPATH=src:$PYTHONPATH
export QT_QPA_PLATFORM=offscreen
python3 -m pytest tests/test_business_pixmap.py
