import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from evo.util.render import save_video
import re


def read_video_cv2(file, n_frames=1000):
    cap = cv2.VideoCapture(file)
    all = []
    i = 0
    while cap.isOpened() and i < n_frames:
        ret, frame = cap.read()
        arr = np.array(frame)
        all.append(arr)
        i += 1
    return np.array(all)


videos_dir = 'experiments/runs/right_side_survive_v1/run_2023-09-15_19-39-11_8773485453367/videos'
video_files = sorted(Path(videos_dir).glob('*.mp4'))


def get_generation(video):
    generation = video.stem.split('_')[1]
    return int(re.sub(r'\D', '', generation))


generations = [get_generation(video) for video in video_files]
render_generations = [0, 5, 15]

assert all(generation in generations for generation in render_generations), \
    'Not all render generations are in the video files'

video_frames = [
    read_video_cv2(str(file), n_frames=100)
    for generation, file in zip(generations, video_files)
    if generation in render_generations
]
generations = [
    generation
    for generation in generations
    if generation in render_generations
]

plot_frames = []
for frame_group in zip(*video_frames):
    fig, axs = plt.subplots(1, len(frame_group), figsize=(5 * len(frame_group), 5))
    for i, (frame, generation) in enumerate(zip(frame_group, generations)):
        axs[i].imshow(frame)
        axs[i].axis('off')
        axs[i].set_title(f'Generation {generation}')
    fig.tight_layout(pad=1.5)
    fig.canvas.draw()
    plot_frames.append(np.array(fig.canvas.renderer._renderer))
    fig.clf()
    plt.close(fig)

save_video(plot_frames, 'videos', format='gif', fps=10)
