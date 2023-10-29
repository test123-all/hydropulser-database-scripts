import csv
from pathlib import Path

import uuid6


def main(quanitity_ofUUID7s :int = 10):
    # Get the directory path of this file
    directory_path = Path(__file__).parent.resolve()
    generated_directory = Path(f"{directory_path}/_generated_UUIDs/")

    try:
        generated_directory.mkdir()
    except FileExistsError:
        pass

    saved_data_filepath = Path(f"{generated_directory}/saved_UUID7s.csv")
    with open(saved_data_filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['UUID7s'])

        uuid_set = set()
        for i in range(quanitity_ofUUID7s):
            unique_id = uuid6.uuid7()
            writer.writerow([unique_id])
            uuid_set.add(unique_id)

    print(f"Successfuly written {len(uuid_set)} UUID7s into the file at the path '{saved_data_filepath.resolve()}'")



if __name__ == '__main__':
    main()
