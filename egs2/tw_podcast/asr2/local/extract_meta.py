# Copyright 2021  Xiaomi Corporation (Author: Yongqing Wang)
#                 Mobvoi Inc(Author: Di Wu, Binbin Zhang)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import os
import sys
import librosa


def get_args():
    parser = argparse.ArgumentParser(
        description="""
      This script is used to process raw youtube podcasts,
      where the long wav is splitinto segments
      """
    )
    parser.add_argument("raw_audio_dir", help="""Audio dir of raw yt data""")
    parser.add_argument("output_dir", help="""Output dir for prepared data""")

    args = parser.parse_args()
    return args


def meta_analysis(raw_audio_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    audio_file_list = [os.path.join(raw_audio_dir, audio_file)  for audio_file in os.listdir(raw_audio_dir)]
    assert len(audio_file_list) >= 10, f"{raw_audio_dir} should have at least 10 samples"
    
    # TODO: Check if the files are all audio file (given the suffix)
    train_end_idx = int(len(audio_file_list) * 0.8)
    dev_end_idx = int(len(audio_file_list) * 0.9)
    test_end_idx = len(audio_file_list) - 1

    if audio_file_list is not None:
        aid = 0
        with open(f"{output_dir}/text", "w") as utt2text, open(
            f"{output_dir}/segments", "w"
        ) as segments, open(f"{output_dir}/utt2dur", "w") as utt2dur, open(
            f"{output_dir}/wav.scp", "w"
        ) as wavscp, open(
            f"{output_dir}/utt2subsets", "w"
        ) as utt2subsets, open(
            f"{output_dir}/reco2dur", "w"
        ) as reco2dur:
            for long_audio_path in audio_file_list:
                aid += 1
                try:
                    # long_audio_path = os.path.realpath(
                    #     os.path.join(input_dir, long_audio["path"])
                    # )
                    # aid = long_audio["aid"]
                    assert os.path.exists(long_audio_path)
                    segments_lists = []
                    duration = int(librosa.get_duration(filename=long_audio_path))
                    for i in range(0, duration, 30):
                        segments_lists.append({
                            'sid': str.zfill(str(aid), 5) + '-' + str(i//30),
                            'begin_time': i,
                            'end_time': min(i+30, duration),
                            'text': '',
                        })
                except AssertionError:
                    print(
                        f"""Warning: {long_audio_path} something is wrong,
                                maybe AssertionError, skipped"""
                    )
                    continue
                except Exception as e:
                    print(
                        f"""Warning: {long_audio_path} something is wrong, maybe the
                                error path: {long_audio_path}, skipped
                            {e}"""
                    )
                    continue
                else:
                    wavscp.write(f"{aid}\t{long_audio_path}\n")
                    reco2dur.write(f"{aid}\t{duration}\n")
                    for segment_file in segments_lists:
                        try:
                            sid = segment_file["sid"]
                            start_time = segment_file["begin_time"]
                            end_time = segment_file["end_time"]
                            dur = end_time - start_time
                            text = segment_file["text"]

                            if aid <= train_end_idx:
                                segment_subsets = 'train'
                            elif aid <= dev_end_idx:
                                segment_subsets = 'dev'
                            else:
                                segment_subsets = 'test'
                        except Exception:
                            print(
                                f"""Warning: {segment_file} something
                                        is wrong, skipped"""
                            )
                            continue
                        else:
                            utt2text.write(f"{sid}\t{text}\n")
                            segments.write(
                                f"{sid}\t{aid}\t{start_time}\t{end_time}\n"
                            )
                            utt2dur.write(f"{sid}\t{dur}\n")
                            segment_sub_names = segment_subsets
                            utt2subsets.write(f"{sid}\t{segment_sub_names}\n")


def main():
    args = get_args()

    meta_analysis(args.raw_audio_dir, args.output_dir)


if __name__ == "__main__":
    main()
