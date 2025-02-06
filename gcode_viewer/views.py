import json
from django.http import JsonResponse
from .gcode_parser import ReadLines, Get_Coords, GcodeError
from django.shortcuts import render

def index(request):

    if request.method == 'GET':

        return render(request, 'gcode_viewer/index.html')
    
    if request.method == "POST":

        try:

            data = request.body.decode('utf-8')
            python_obj = json.loads(data)
            new_data = python_obj.get('gcode')

            find_error = ReadLines(new_data)  #find type error
            result_error = find_error.read_G_code()
            print(result_error)

            element = Get_Coords(new_data)  #if error is absent
            result = element.find_coords()
            print(result)
            return JsonResponse({'result': result})
        
        except GcodeError as gcodeExeption:

            print(gcodeExeption)
            return JsonResponse({'error': str(gcodeExeption)}, status=500)

        except Exception as e:

            return JsonResponse({'error': str(e)}, status=400)
        
        