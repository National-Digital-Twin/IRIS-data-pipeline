from telicent_lib import Record, RecordUtils

def make_passthrough(source_topic: str):
    def passthrough(record: Record) -> Record:
        key = f"{source_topic}|{record.key or ''}"
        out = Record(record.headers, key, record.value, None)
        out = RecordUtils.add_header(out, "source_topic", source_topic)
        return out
    return passthrough
