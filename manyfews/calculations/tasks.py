from celery import Celery, shared_task
from celery.schedules import crontab
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from .zentra import zentraReader, offsetTime, aggregateZentraData
from .gefs import dataBaseWriter
from django.conf import settings
from .models import (
    InitialCondition,
    RiverFlowCalculationOutput,
    RiverFlowPrediction,
    AggregatedZentraReading,
)
from .generate_river_flows import (
    prepareGEFSdata,
    prepareInitialCondition,
    GenerateRiverFlows,
)
from datetime import datetime, timedelta, timezone
import os
from tqdm import trange
import numpy as np

app = Celery()

import logging

logger = logging.getLogger(__name__)


@shared_task(name="calculations.hello_celery")
def hello_celery():
    """
    This is an example of a task that can be scheduled via celery.
    """
    logger.info("Hello logging from celery!")


@shared_task(name="calculations.prepareGEFS")
def prepareGEFS():
    """
    This function is developed to extract necessary GEFS forecast data sets
    into Database for running the River Flows model
    """
    # prepare GEFS data
    dt = float(settings.MODEL_TIMESTEP)
    forecastDays = int(settings.GEFS_FORECAST_DAYS)
    dataBaseWriter(dt=dt, forecastDays=forecastDays)


@shared_task(name="calculations.prepareZentra")
def prepareZentra(backDay=1):
    """
    This function is developed to extract daily necessary Zentra cloud observation data sets
    into Database and aggregate data for running the River Flows model.

    :param backDay: the number of previous days you want to extract from zentra cloud. (default = 1)
    For each day: the data is from 00:00 ---> 23:55
    """

    # get serial number
    stationSN = settings.STATION_SN

    # prepare start_time and end_time
    timeInfo = offsetTime(backDays=backDay)
    startTime = timeInfo[0]
    endTime = timeInfo[1]

    # prepare Zentra Cloud data
    zentraReader(startTime=startTime, endTime=endTime, stationSN=stationSN)

    # aggregate zentra data
    aggregateZentraData(startTime=startTime, endTime=endTime, stationSN=stationSN)


@shared_task(name="calculations.runningGenerateRiverFlows")
def runningGenerateRiverFlows(predictionDate, dataLocation):
    """
    This function is developed to prepare data and running models for generating river flows,
    and save the next day's initial condition, River flow, Rainfall, and potential evapotranspiration
    into DB.

    :param beginDate: the date information of input data.
    :param dataLocation: the location information of input data
    :return none.
    """
    projectPath = os.path.abspath(
        os.path.join((os.path.split(os.path.realpath(__file__))[0]), "../../")
    )

    dataFileDirPath = os.path.join(projectPath, "Data")
    parametersFilePath = os.path.join(
        dataFileDirPath, "RainfallRunoffModelParameters.csv"
    )

    # plus time zone information
    predictionDate = datetime.astimezone(
        predictionDate, tz=timezone(timedelta(hours=0))
    )

    # prepare GEFS data for model.
    gefsData = prepareGEFSdata(date=predictionDate, location=dataLocation)

    # prepare initial condition data for model.
    initialConditionData = prepareInitialCondition(
        date=predictionDate, location=dataLocation
    )

    # run model.
    dt = float(settings.MODEL_TIMESTEP)
    riverFlowsData = GenerateRiverFlows(
        dt=dt,
        predictionDate=predictionDate,
        gefsData=gefsData,
        F0=initialConditionData,
        parametersFilePath=parametersFilePath,
    )

    # riverFlowsData[0] ====> Q: River flow (m3/s).
    # riverFlowsData[1] ====> qp: Rainfall (mm/day).
    # riverFlowsData[2] ====> Ep: Potential evapotranspiration (mm/day).
    # riverFlowsData[3] ====> F0: intial condition data for next day.

    riverFlows = riverFlowsData[0]
    qp = riverFlowsData[1]
    Ep = riverFlowsData[2]
    F0 = riverFlowsData[3]  # next day's initial condition

    # import the next day's initial condition data F0 into DB.
    # ('calculations_initialcondition' table)
    nextDay = predictionDate + timedelta(days=1)

    for i in range(len(F0[:, 0])):
        nextDayInitialCondition = InitialCondition(
            date=nextDay,
            location=dataLocation,
            storage_level=F0[i, 0],
            slow_flow_rate=F0[i, 1],
            fast_flow_rate=F0[i, 2],
        )
        nextDayInitialCondition.save()

    for i in range(qp.shape[0]):
        # save qp and Eq and into DB.
        # ( 'calculations_riverflowcalculationoutput' table)
        forecastTime = predictionDate + timedelta(days=i * dt)
        riverFlowCalculationOutputData = RiverFlowCalculationOutput(
            prediction_date=predictionDate,
            forecast_time=forecastTime,
            location=dataLocation,
            rain_fall=qp[i],
            potential_evapotranspiration=Ep[i],
        )
        riverFlowCalculationOutputData.save()

        # save Q into DB.
        # ('calculations_riverflowprediction' table)
        for j in range(riverFlows.shape[1]):
            riverFlowPredictionData = RiverFlowPrediction(
                prediction_index=j,
                calculation_output=riverFlowCalculationOutputData,
                river_flow=riverFlows[i, j],
            )
            riverFlowPredictionData.save()


@shared_task(name="calculations.initialModelSetUp")
def initialModelSetUp():
    """ """
    stationSN = settings.STATION_SN
    backDays = int(settings.INITIAL_BACKTIME)

    # Prepare Zentra data from 365 days ago
    # for back in trange(backDays, 0, -1):
    # prepare zentra data and aggregate them
    # prepareZentra(back)

    projectPath = os.path.abspath(
        os.path.join((os.path.split(os.path.realpath(__file__))[0]), "../../")
    )

    dataFileDirPath = os.path.join(projectPath, "Data")
    parametersFilePath = os.path.join(
        dataFileDirPath, "RainfallRunoffModelParameters.csv"
    )
    InitialConditionFile = os.path.join(
        dataFileDirPath, "RainfallRunoffModelInitialConditions.csv"
    )
    initialConditionData = np.loadtxt(
        open(InitialConditionFile), delimiter=",", usecols=range(3)
    )

    # plus time zone information

    # prepare Zentra data for model.
    startTime = datetime(year=2021, month=3, day=13, hour=0, minute=0, second=0)
    endTime = startTime + timedelta(days=15.75)

    startTime = datetime.astimezone(startTime, tz=timezone(timedelta(hours=0)))
    endTime = datetime.astimezone(endTime, tz=timezone(timedelta(hours=0)))

    aggregatedZentraData = AggregatedZentraReading.objects.filter(
        date__range=(startTime, endTime)
    )

    RHList = []
    minTemperatureList = []
    maxTemperatureList = []
    uWindList = []
    vWindList = []
    precipitationList = []

    for data in aggregatedZentraData:
        RHList.append(data.relative_humidity)
        minTemperatureList.append(data.min_temperature)
        maxTemperatureList.append(data.max_temperature)
        uWindList.append(data.wind_u)
        vWindList.append(data.wind_v)
        precipitationList.append(data.precipitation)

    aggregatedZentraDataList = list(
        zip(
            RHList,
            maxTemperatureList,
            minTemperatureList,
            uWindList,
            vWindList,
            precipitationList,
        )
    )

    aggregatedZentra = np.array(aggregatedZentraDataList)

    print(np.shape(aggregatedZentra))

    dt = float(settings.MODEL_TIMESTEP)

    riverFlowsData = GenerateRiverFlows(
        dt=dt,
        gefsData=aggregatedZentra,
        F0=initialConditionData,
        parametersFilePath=parametersFilePath,
    )

    F0 = riverFlowsData[3]

    for i in range(len(aggregatedZentra)):
        print(aggregatedZentra[i, :])

    print(F0[0, :])


@shared_task(name="calculations.dailyModelUpdate")
def dailyModelUpdate():

    print("set up daily model update")


# initialModelSetUp()

# prepareGEFS()
