# pages/views.py
from django.shortcuts import render, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from pages.models import Item, ToDoList
from django.shortcuts import render, redirect
from .forms import RegisterForm
import plotly.graph_objs as go
import pandas as pd
import requests
from datetime import date

df_columns = {
    'ADJOE': 'Adj. Offensive Efficiency',
    'ADJDE': 'Adj. Defensive Efficiency',
    'TORD': 'Defensive Turnover Rate',
    'DRB': 'Defensive Rebound Rate',
    'WIN_PCT': 'Win Percentage'
}

def scores(request):

    # Set the API endpoint URL
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"

    # Set the query parameters to get information for the NCAA Men's Basketball Tournament First Four
    params = {
        "dates": '20230317',
        "limit": "100",  # limit the number of results to 100
    }

    # Make the GET request and get the JSON response
    response = requests.get(url, params=params)
    json_response = response.json()
    # print(json_response)
    scores = []

    # # Extract the shortName, description, and detail fields for each event in the response
    for event in json_response["events"]:
        short_name = event["shortName"]
        score1 = event["competitions"][0]["competitors"][0]["score"]
        score2 = event["competitions"][0]["competitors"][1]["score"]
        cur_score = f"{score1} - {score2}"
        description = event["status"]["type"]["description"]
        detail = event["status"]["type"]["shortDetail"]

        scores.append({'shortName': short_name, 'current_score': cur_score, 'description': description, 'shortDetail': detail})
        # Print the extracted fields
        # print(f"Short name: {short_name}")
        # print(f"Description: {description}")
        # print(f"Detail: {detail}")
        # print("\n")
    return render(request, 'scores.html', {'scores': scores})

def secretArea(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('message',
               kwargs={'msg': "Please login to access this page.",
                       'title': "Login required."}, ))
    return render(request, 'secret.html', {'useremail': request.user.email })


def predictionsPageView(request):
    # offense_fields = ['ADJUSTED OFFENSIVE EFFICIENCY (ADJOE)', 'OFFENSIVE REBOUND RATE (ORB)', 'FREE THROW RATE (FTR)', '2-POINT SHOOTING % (2P_O)']
    # defense_fields = ['DEFENSIVE TURNOVER RATE (TORD)', 'ADJUSTED OFFENSIVE EFFICIENCY (ADJDE)', 'DEFENSIVE EFFECTIVE FG % (EFG_D)', 'DEFENSIVE REBOUND RATE (DRB)', 'DEFENSIVE 2-POINT SHOOTING % (2P_D)', 'DEFENSIVE 2-POINT SHOOTING % (3P_D)']
    # total_fields = ['WINS', 'GAMES PLAYED']
    # other = ['BARTHAG']
    # context = {'off_fields': offense_fields, 'def_fields': defense_fields, 'tot_fields': total_fields, 'other': other}
    return render(request, 'predictions.html', df_columns)

def message(request, msg, title):
    return render(request, 'message.html', {'msg': msg, 'title': title })

def register(response):
    # Handle POST request.
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('message',
                                                kwargs={'msg': "Your are registered.", 'title': "Success!"}, ))
    # Handle GET request.
    else:
        form = RegisterForm()
    return render(response, "registration/register.html", {"form":form})


def homePageView(request):
    # return request object and specify page.
    return render(request, 'home.html', {
        'mynumbers':[1,2,3,4,5,6,],
        'firstName': 'Josef',
        'lastName': 'Murillo'})


def aboutPageView(request):
    context = request.session.get('context')
    school_name = context.get('school')

    # your code here
    print(f"context stuff {context.items()}")
    # Read in the CSV data
    df = pd.read_csv('C:\\Users\\Josef\\Documents\\BCIT\\CST Term 4\\Term 4 Homework\\COMP 4949 - Big Data Analytics\\Lesson 8\\helloworld\\pages\\cbb.csv')

    columns = ['TORD', 'DRB']

    # # Create a histogram using Plotly
    trace = go.Histogram(x=df['W'], nbinsx=40)

    data = [trace]
    layout = go.Layout(title='Wins')
    fig = go.Figure(data=data, layout=layout)
    hist_div = fig.to_html(full_html=False)

    # Create a list of box plots for each column
    plot_divs = []
    for col in columns:
        x_value = context.get(col.lower())
        print(f"xvalue {x_value}")
        trace = go.Box(x=df[col], name=col)
        trace2 = go.Scatter(x=[x_value], y=[col], mode='markers', name=school_name)
        layout = go.Layout(title=f'{df_columns[col]}')
        fig = go.Figure(data=[trace, trace2], layout=layout)
        plot_div = fig.to_html(full_html=False)
        plot_divs.append(plot_div)

    # Create a scatter plot using Plotly
    trace = go.Scatter(x=df['ADJOE'], y=df['ADJDE'], mode='markers', name='Scatter Plot')
    trace2 = go.Scatter(x=[context.get('adjoe')], y=[context.get('adjde')], mode='markers', name=school_name)
    layout = go.Layout(title='Scatter Plot', xaxis=dict(title='Adjusted Offensive Eff.'), yaxis=dict(title='Adjusted Defensive Eff.'), width=800,
                       height=800, autosize=False)
    fig = go.Figure(data=[trace, trace2], layout=layout)
    scatter_plot_div = fig.to_html(full_html=False)

    # Pass the plot to the template
    return render(request, 'about.html', {'hist_div': hist_div, 'plot_divs': plot_divs, 'scatter_plot_div': scatter_plot_div})


def namePageView(request):
    return render(request, 'josef.html')

def predictions_post(request):
    try:
        adjoe = float(request.POST['ADJOE'])
        drb = float(request.POST['DRB'])
        adjde = float(request.POST['ADJDE'])
        tord = float(request.POST['TORD'])
        w = float(request.POST['W'])
        g = float(request.POST['G'])
        win_pct = w / g
        school = request.POST['school']
        context = {
            'adjoe': adjoe,
            'drb': drb,
            'adjde': adjde,
            'tord': tord,
            'w': w,
            'g': g,
            'win_pct': win_pct,
            'school': school,
        }
        # print(context.items())
        request.session['context'] = context
        return redirect('results')
    except (ValueError, KeyError):
        return render(request, 'predictions.html')



def homePost(request):
    # Use request object to extract choice.

    choice = -999
    gmat = -999

    try:
        # Extract value from request object by control name.
        currentChoice = request.POST['choice']
        gmatStr = request.POST['gmat']

        # Crude debugging effort.
        print("*** Years work experience: " + str(currentChoice))
        choice = int(currentChoice)
        gmat = float(gmatStr)
    # Enters 'except' block if integer cannot be created.
    except:
        return render(request, 'home.html', {
            'errorMessage': '*** The data submitted is invalid. Please try again.',
            'mynumbers': [1, 2, 3, 4, 5, 6, ]})
    else:
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('results', kwargs={'choice': choice, 'gmat': gmat}, ))


import pickle
import sklearn  # You must perform a pip install.
import pandas as pd


# def results(request, choice, gmat):
#     # load saved model
#     with open('../helloworld/model_pkl', 'rb') as f:
#         loadedModel = pickle.load(f)
#
#     # Create a single prediction.
#     singleSampleDf = pd.DataFrame(columns=['gmat', 'work_experience'])
#
#     workExperience = float(choice)
#     print("*** GMAT Score: " + str(gmat))
#     print("*** Years experience: " + str(workExperience))
#     singleSampleDf = singleSampleDf.append({'gmat': gmat,
#                                             'work_experience': workExperience},
#                                            ignore_index=True)
#
#     singlePrediction = loadedModel.predict(singleSampleDf)
#
#     print("Single prediction: " + str(singlePrediction))
#
#     return render(request, 'results.html', {'choice': workExperience, 'gmat': gmat,
#                                             'prediction': singlePrediction})

def results(request):
    # print("*** Inside results()")
    context = request.session.get('context')
    # print(context.get('adjoe'))
    # load saved model
    with open('../helloworld/django_model_pkl', 'rb') as f:
        loadedModel = pickle.load(f)

    with open('../helloworld/django_scaler.sav', 'rb') as s:
        scaler = pickle.load(s)

    # Create a single prediction.
    singleSampleDf = pd.DataFrame(columns=[col for col in df_columns.keys()])
    print(df_columns.keys())
    singleSampleDf = singleSampleDf.append({'ADJOE': context.get('adjoe'),
                                            'ADJDE': context.get('adjde'),
                                            'TORD': context.get('tord'),
                                            'DRB': context.get('drb'),
                                            'WIN_PCT': context.get('win_pct'),
                                            },
                                           ignore_index=True)
    singleSampleDf = scaler.transform(singleSampleDf)

    singlePrediction = loadedModel.predict(singleSampleDf)
    #
    # print("Single prediction: " + str(singlePrediction))
    context['prediction'] = singlePrediction[0]

    print(context.items())
    return render(request, 'results.html', context)


def todos(request):
    print("*** Inside todos()")
    items = Item.objects
    itemErrandDetail = items.select_related('todolist')
    print(itemErrandDetail[0].text)
    # print(itemErrandDetail[0].todolist.task)
    return render(request, 'ToDoItems.html',
                {'ToDoItemDetail': itemErrandDetail})
