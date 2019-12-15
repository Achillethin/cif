import os
import datetime
import json
import sys

import torch

from tensorboardX import SummaryWriter


class Tee:
    def __init__(self, primary_file, secondary_file):
        self.primary_file = primary_file
        self.secondary_file = secondary_file

        self.encoding = self.primary_file.encoding

    def fileno(self):
        return self.primary_file.fileno()

    def write(self, data):
        self.primary_file.write(data)
        self.secondary_file.write(data)

    def flush(self):
        self.primary_file.flush()
        self.secondary_file.flush()


class Writer:
    def __init__(self, logdir_root, tag_group):
        os.makedirs(logdir_root, exist_ok=True)

        timestamp = f"{datetime.datetime.now().strftime('%b%d_%H-%M-%S')}"
        logdir = os.path.join(logdir_root, timestamp)

        self._writer = SummaryWriter(logdir=logdir)

        self._tag_group = tag_group

        self._stdout = open(os.path.join(self._logdir, "stdout"), "w")
        self._stderr = open(os.path.join(self._logdir, "stderr"), "w")
        sys.stdout = Tee(primary_file=sys.stdout, secondary_file=self._stdout)
        sys.stderr = Tee(primary_file=sys.stderr, secondary_file=self._stderr)

    def write_scalar(self, tag, scalar_value, global_step=None):
        self._writer.add_scalar(self._tag(tag), scalar_value, global_step=global_step)

    def write_image(self, tag, img_tensor, global_step=None):
        self._writer.add_image(self._tag(tag), img_tensor, global_step=global_step)

    def write_figure(self, tag, figure, global_step=None):
        self._writer.add_figure(self._tag(tag), figure, global_step=global_step)

    def write_hparams(self, hparam_dict=None, metric_dict=None):
        self._writer.add_hparams(hparam_dict=hparam_dict, metric_dict=metric_dict)

    def write_json(self, tag, data):
        text = json.dumps(data, indent=4)

        self._writer.add_text(
            self._tag(tag),
            4*" " + text.replace("\n", "\n" + 4*" ") # Indent by 4 to ensure codeblock formatting
        )

        json_path = os.path.join(self._logdir, f"{tag}.json")

        with open(json_path, "w") as f:
            f.write(text)

    def write_textfile(self, tag, text):
        path = os.path.join(self._logdir, f"{tag}.txt")
        with open(path, "w") as f:
            f.write(text)

    def write_checkpoint(self, tag, data):
        os.makedirs(self._checkpoints_dir, exist_ok=True)
        checkpoint_path = os.path.join(self._checkpoints_dir, f"{tag}.pt")

        tmp_checkpoint_path = os.path.join(
            os.path.dirname(checkpoint_path),
            f"{os.path.basename(checkpoint_path)}.tmp"
        )

        torch.save(data, tmp_checkpoint_path)
        # rename is atomic, so we guarantee our checkpoints are always good
        os.rename(tmp_checkpoint_path, checkpoint_path)

    @property
    def _checkpoints_dir(self):
        return os.path.join(self._logdir, "checkpoints")

    @property
    def _logdir(self):
        return self._writer.logdir

    def _tag(self, tag):
        return f"{self._tag_group}/{tag}"


class DummyWriter:
    def write_scalar(self, tag, scalar_value, global_step=None):
        pass

    def write_image(self, tag, img_tensor, global_step=None):
        pass

    def write_figure(self, tag, figure, global_step=None):
        pass

    def write_hparams(self, hparam_dict=None, metric_dict=None):
        pass

    def write_json(self, tag, data):
        pass

    def write_checkpoint(self, tag, data):
        pass

    def write_textfile(self, tag, text):
        pass
