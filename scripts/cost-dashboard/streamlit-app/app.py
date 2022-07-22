import boto3
from datetime import date, datetime

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


# st.set_page_config(page_icon="📥", page_title="Download App")

# def icon(emoji: str):
#     """Shows an emoji as a Notion-style page icon."""
#     st.write(
#         f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
#         unsafe_allow_html=True,
#     )
    
client = boto3.client('ce')

# time_period={'Start': '2022-05-01', 'End': '2022-07-20'}

def get_dataframe_from_cost_explorer(start_date, end_date, granularity):
    start_date_string=start_date.strftime("%Y-%m-%d")
    end_date_string=end_date.strftime("%Y-%m-%d")
    time_period={'Start': start_date_string, 'End': end_date_string}
    print(time_period)
    response = client.get_cost_and_usage(
                TimePeriod=time_period,
                Granularity=granularity, #'DAILY',
                Filter={
                    'Dimensions' : {
                        'Key'    : 'SERVICE',
                        'Values' : ['Amazon SageMaker']
                    }
                },
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {
                        'Type':'DIMENSION',
                        'Key' :'USAGE_TYPE'
                    }
                ]
            )

#     print(response)
    dfs=[]
    for i, cost_per_day in enumerate(response['ResultsByTime']):
        usage_type=[]
        amount=[]
        timestamp=cost_per_day['TimePeriod']['Start']
#         timestamp_dt=datetime.strptime(timestamp, "%Y-%m-%d")
        for j, cost_per_usage in enumerate(cost_per_day['Groups']):
            usage_type.append(cost_per_usage['Keys'][0])
            amount.append(cost_per_usage['Metrics']['UnblendedCost']['Amount'])
            
#         amount=np.random.rand(1,len(amount))
        df_tmp=pd.DataFrame(index=[timestamp], 
                            columns=usage_type, 
                            data=[amount], 
#                             data=amount,
                            dtype=float)
        dfs.append(df_tmp)  
    df=pd.concat(dfs)
#     df["date"] = df.index.astype("datetime64[ns]")
    
    return df

def monthly_charges(start_date, end_date):
    df = get_dataframe_from_cost_explorer(start_date, end_date, 'MONTHLY')

    return df


def daily_charges(start_date, end_date):
    df = get_dataframe_from_cost_explorer(start_date, end_date, 'DAILY')

    return df


# def pandasamlit_downloads(source, x="date", y="USE2-Host:ml.m4.xlarge"):
#     # Create a selection that chooses the nearest point & selects based on x-value
#     source
#     hover = alt.selection_single(
#         fields=[x],
#         nearest=True,
#         on="mouseover",
#         empty="none",
#     )

#     lines = (
#         alt.Chart(source)
#         .mark_line(point="transparent")
#         .encode(x=x, y=y)
# #         .transform_calculate(color='datum.delta < 0 ? "red" : "green"')
#     )

#     # Draw points on the line, highlight based on selection, color based on delta
#     points = (
#         lines.transform_filter(hover)
#         .mark_circle(size=65)
#         .encode(color=alt.Color("color:N", scale=None))
#     )

#     # Draw an invisible rule at the location of the selection
#     tooltips = (
#         alt.Chart(source)
#         .mark_rule(opacity=0)
#         .encode(
#             x=x,
#             y=y,
#             tooltip=[x, y],#, alt.Tooltip("delta", format=".2%")],
#         )
#         .add_selection(hover)
#     )

#     return (lines + points + tooltips).interactive()


def main():

    # Note that page title/favicon are set in the __main__ clause below,
    # so they can also be set through the mega multipage app (see ../pandas_app.py).

    col1, col2 = st.columns(2)

    with col1:
        start_date, end_date = st.date_input(
            "Select start date",
            [date(2022, 1, 1), date.today()],
            min_value=datetime.strptime("2022-01-01", "%Y-%m-%d"),
            max_value=datetime.now(),
        )
        
    with col2:
        time_frame = st.selectbox(
            "Select daily or monthly downloads", ("daily", "monthly")
        )

#     with col3:
#         service = st.selectbox(
#             "Select services to review", ("Amazon SageMaker")
#         )

    # PREPARING DATA FOR DAILY AND MONTHLY
    if time_frame == "daily":
        df = daily_charges(start_date, end_date)
    else:
        df = monthly_charges(start_date, end_date)        

    all_usage_types = df.columns.unique().tolist()
    print(all_usage_types)
    usage_types = st.multiselect("Choose usage types to visualize", all_usage_types, all_usage_types[:3])

    st.header("SageMaker Cost Explorer")
    
#     source = source[source.symbol.isin(symbols)]
#     chart = chart.get_chart(source)
#     st.altair_chart(chart, use_container_width=True)

#     st.altair_chart(pandasamlit_downloads(df), use_container_width=True)

    st.bar_chart(df[usage_types])
    
    if st.checkbox("Show raw data"):
        st.subheader("Raw data")
        st.write(df)
    
    
    st.title("Service charges")
    st.write(
        "Metrics on how often Pandas is being downloaded from PyPI (Python's main "
        "package repository, i.e. where `pip install pandas` downloads the package from)."
    )
main()