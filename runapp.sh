cd website
gunicorn --bind  0.0.0.0:5000 app:app & python3 /home/Darterone/Lora/AmanLoraProj/motion_cam_sqlite_v3.0.py &  python3 /home/Darterone/Lora/AmanLoraProj/transtrail1\(final\).py
