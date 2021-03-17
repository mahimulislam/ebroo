from django.http import HttpResponseForbidden, FileResponse
from django.shortcuts import render, HttpResponse
# Celery Task
import pandas as pd
from .tasks import ProcessDownload
import time
import celery_progress_demo
import os
from pathlib import Path
def demo_view(request):
    # If method is POST, process form data and start task
    if request.method == 'POST':
        # Create Task
        file = request.FILES["myFile"]
        csv1 = pd.read_csv(file)
        urllists = csv1["urls"]

        urllist = urllists.to_list()

        # Get ID

        #process = ProcessDownload.apply_async(args=(urllist,))  # mytask.delay(arg1)
        process = ProcessDownload.delay(urllist)
        task_id = process.task_id
        # Print Task ID
        filename=str(task_id)+".csv"
        print(f'Celery Task ID: {task_id}')
        print("BODDA AMI EKHANE")
        print(filename)
        # Return demo view with Task ID
        while (True):
            time.sleep(5)
            state = process.state
            print(state)
            if state == ("SUCCESS"):
                break
        if state==("SUCCESS"):
            print("Eine AIA PORSI")
            print(filename)
            cwd = Path.cwd()
            textfile = str(cwd)+'/'+filename
            print(textfile)
            response = FileResponse(open(textfile, 'rb'))

            return response
        else:
            return render(request, 'progress.html', {'task_id': task_id})
    else:
        # Return demo view
        return render(request, 'progress.html', {})
