import struct

import scrapy
import os
import logging
from scrapy.pipelines.images import FilesPipeline


from scrapyManga.items import MetaFileItem
from scrapyManga.settings import FILES_STORE

logger = logging.getLogger(__name__)


class ScrapymangaPipeline(FilesPipeline):

    global_path = FILES_STORE
    received = 0
    count = 0
    count_done = 0

    def parse_mri_data_to_webp_buffer(self, data):
        size_list = [0] * 4
        size = len(data)
        header_size = size + 7

        # little endian byte representation
        # zeros to the right don't change the value
        for i, byte in enumerate(struct.pack("<I", header_size)):
            size_list[i] = byte

        buffer = [
            82,  # R
            73,  # I
            70,  # F
            70,  # F
            size_list[0],
            size_list[1],
            size_list[2],
            size_list[3],
            87,  # W
            69,  # E
            66,  # B
            80,  # P
            86,  # V
            80,  # P
            56,  # 8
        ]

        for bit in data:
            buffer.append(101 ^ bit)
        return buffer

    def convert_mri(self, mri_path, delete=True):
        full_mri_path = self.global_path + "/" + mri_path
        f = open(full_mri_path, "rb")
        data = f.read()
        f.close()
        decoded = self.parse_mri_data_to_webp_buffer(data)
        out_webp = full_mri_path.replace(".mri", ".webp")
        out_file = open(out_webp, "wb")
        out_file.write(bytes(decoded))
        out_file.close()
        if delete:
            os.remove(full_mri_path)

    def move_or_delete(self, path_from, path_to):
        global_path_from = self.global_path + "/" + path_from
        global_path_to = self.global_path + "/" + path_to
        if not os.path.exists(global_path_from):
            logger.warning("File not found %s", global_path_from)
            return False
        if os.path.exists(global_path_to):
            os.remove(global_path_from)
        else:
            head_path, _ = os.path.split(global_path_to)
            os.makedirs(head_path, exist_ok=True)
            os.rename(global_path_from, global_path_to)
        return True

    def file_exists(self, file_path):
        return os.path.isfile(file_path)

    # Executed before
    def get_media_requests(self, item, info):
        if not isinstance(item, MetaFileItem):
            return item
        file_path = self.global_path + "/" + item["file_path"]
        for file_url in item["file_urls"]:
            file_path_not_mri = file_path.replace(".mri", ".webp")
            self.received += 1
            if not self.file_exists(file_path_not_mri):
                self.count += 1
                yield scrapy.Request(file_url)

    # Executed after
    def item_completed(self, results, item, info):
        if not isinstance(item, MetaFileItem):
            return item
        if "verbose" in item:
            verbose = item["verbose"]
        else:
            verbose = False
        for ok, x in results:
            if ok:
                file_from = x["path"]
                file_to = item["file_path"]
                self.count_done += 1
                if verbose:
                    logger.info("PICTURE: " + file_to)
                no_error = self.move_or_delete(file_from, file_to)
                if no_error and file_to.endswith(".mri"):
                    self.convert_mri(file_to)
            else:
                logger.error("NOT SCRAPED: " + str(x))
        return None

    def close_spider(self, spider):
        logger.info(
            "Received, %s items, downloaded %s, done %s",
            self.received,
            self.count,
            self.count_done,
        )
