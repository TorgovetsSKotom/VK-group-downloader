# VK-group-downloader

Downloads all images from posts in the VK.com group, written in Selenium

## Features

- Upload an image from a post
- Save the URL of the image in a log file to skip it next time
- Choise number cycle load posts when simulating page scrolling
- Select the number of posts loading cycles when simulating page scrolling

## Usage

python vk_group_parser.py [-h] [--url URL] [--output PATH] [--num_cycle NUM] [--log_dir LOG]

options:

| -h, --help              | show this help message and exit |
| ----------------------- | ------------------------------- |
| --url URL, -u URL       | URL of the VK group             |
| --output PATH, -o PATH  | Path to save images             |
| --num_cycle NUM, -n NUM | Number cycle load new posts     |
| --log_dir LOG, -l LOG   | Path to save log                |