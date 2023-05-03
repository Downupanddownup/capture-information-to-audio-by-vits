from asyncio.windows_events import NULL
import json


class Role:
    def __init__(self, role, language, speaker_id, noise_scale, noise_scale_w, length_scale):
        self.role = role
        self.language = int(language)
        self.speaker_id = int(speaker_id)
        self.noise_scale = float(noise_scale)
        self.noise_scale_w = float(noise_scale_w)
        self.length_scale = float(length_scale)

    def print(self):
        print(
            f'role={self.role};language={self.language};speaker_id={self.speaker_id};noise_scale={self.noise_scale};noise_scale_w={self.noise_scale_w};length_scale={self.length_scale};')

    def print_role(self):
        print(f'{self.role}:{self.speaker_id}')

    def get_specker_info(self):
        return f'{self.role}_{self.noise_scale}_{self.noise_scale_w}_{self.length_scale}'.replace('.', '')


class RoleManager:

    def __init__(self):
        self.roles = []
        self._load_voices()

    def get_role(self, speaker_id):
        for role in self.roles:
            if int(role.speaker_id) == speaker_id:
                return role
        return None

    def _load_voices(self):
        with open('./config/voice.json', encoding='utf-8') as f:
            array = json.load(f)
            for item in array:
                role = Role(item['role'], item['language'], item['speaker_id'], item['noise_scale'],
                            item['noise_scale_w'], item['length_scale'])
                self.roles.append(role)

