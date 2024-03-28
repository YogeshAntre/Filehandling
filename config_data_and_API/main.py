from fastapi import FastAPI, HTTPException, Path, Query,Response
from pydantic import BaseModel
import uvicorn,json
import difflib
from enum import Enum
from fastapi.responses import HTMLResponse
app = FastAPI()

class Comparision(BaseModel):
    device1:str
    file1:str
    device2:str
    file2:str


class DeviceEnum(str, Enum):
    device1 = "134.119.179.21"
    device2 = "134.119.179.20"

def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Remove lines containing only '!' and lines starting or ending with whitespace
        #lines = [line.strip() for line in lines if line.strip() ]
        return lines

# #@app.get("/compare-configs/")
# # async def compare_configs(device1: DeviceEnum = Query(..., description="Hostname or device name for the first device"),
# #                           file1: str = Query(..., description="File ID or filename for the first device"),
# #                           device2: DeviceEnum = Query(..., description="Hostname or device name for the second device"),
# #  
# #                          file2: str = Query(..., description="File ID or filename for the second device")):
    
# @app.post("/compare-configs/")
# def compare_configs(data:Comparision):
#     try:
#         if data.file1 == data.file2 :
#                 return {'status' : False, "msg" : "Same file is selected"}
        
#         with open(data.file1, 'r') as f1, open(data.file2, 'r') as f2:
#             config1 = remove_spaces(f1.readlines())

#             config2 = remove_spaces(f2.readlines())

#         #diff = difflib.unified_diff(config1, config2, lineterm='', fromfile=data.file1, tofile=data.file2)
#         #diff=difflib.HtmlDiff().make_file(config1, config2)
        
#         diff = difflib.unified_diff(config1, config2, lineterm=' ', fromfile=data.file1, tofile=data.file2)
#         #print(diff)
#         diff_result = ''
#         for line in diff:
#             # Remove the leading space character if it's a line added or removed
#             if line.startswith(' '):
#                 line = line[1:]
#             # Concatenate the lines
#             diff_result += line

#         print(diff_result)
#         #######################################################################
#         # diff_result = ' '.join(diff)
#         # output_file_path = f"{data.device1}_{data.device2}_diff.txt"
#         # with open(output_file_path, 'w') as output_file:
#         #     output_file.write(diff_result)
#         # if diff_result == []:
#         #     return {"file":'Same Data in file No diffrence in configurations'}
        
#         # data=json.dumps(diff_result,indent=4)
#         # print(data)
#         return {"diff_result":diff_result}
#         #return HTMLResponse(content=data, status_code=200)
#         ##########################################
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="File not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# if __name__ == "__main__":
#      uvicorn.run(app="main:app", host="localhost", port=8001, reload=True)

@app.post("/compare-configs/")
def compare_configs(data: Comparision):
    try:
        if data.file1 == data.file2 :
                return {'status' : False, "msg" : "Same file is selected"}
        config1 = read_file(data.file1)
        config2 = read_file(data.file2)
        diff = difflib.unified_diff(config1, config2, fromfile=data.file1, tofile=data.file2)
        #print('AA',list(diff))
        # Separate lines with a space between two words if present before available
        # diff_result = []
        # for line in diff:
        #     if line.startswith('+') or line.startswith('-'):
        #         # Split line by space and rejoin with a space between two words if present
        #         words = line[1:].split()
        #         if len(words) > 1 and words[1] == 'available':
        #             line = f"{words[0]} {words[1]} {words[2]}" if len(words) > 2 else f"{words[0]} {words[1]}"
        #         #print(line)
        #         diff_result.append(line)
        #     else:
        #         diff_result.append(line)
        
        # Check if there are any differences
        #has_differences = any(line.startswith('+') or line.startswith('-') for line in diff_result)
        
        # if not has_differences:
        #     return {'status': False, "msg": "No differences found between the configurations."}
        
        # Remove trailing newline characters and unnecessary empty lines
        
        diff_result = [line.rstrip('\n') for line in diff if line.strip()]
        # diff_result = []
        # for line in diff:
        #     line = line.rstrip('\n')
        #     if line.strip() and not ('!' in line):
        #         diff_result.append(line)

       # print(diff_result)
        # Return the diff_result as a list of strings without trailing newline characters and unnecessary empty lines
        #diff_result = ' '.join(diff_result)
        # output_file_path = f"{data.device1}_{data.device2}_diff.txt"
        # with open(output_file_path, 'w') as output_file:
        #     output_file.write(''.join(list(diff)))

        return {"diff_result": diff_result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e.filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
     uvicorn.run(app="main:app", host="localhost", port=8001, reload=True)
