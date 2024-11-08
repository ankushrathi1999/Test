
from config.config import get_artificats

artifacts_config = get_artificats()

def get_artifact_videos():
    videos = []
    for artifact in artifacts_config['artifacts']:
        for video in artifact['videos']:
            videos.append({
                **video,
                "artifact": artifact["code"]
            })
    return videos