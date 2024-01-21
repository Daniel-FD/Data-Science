Hi Daniel,

Hope you are well. Matthew here from Upwork.

Attached is my Jupyter notebook. If you can have a look at it before we meet that would be great. I have kept it super simple on purpose. So in another project i would normally, for example, do more EDA, plots , and test other models.

 **Objectives:
** [1] Please have a look and see if the code is MOSTLY correct :)
[2] If i have run SHAP correctly
[3] If i have calculated false positives and negatives correctly

Based on the above i would like to work with you to teach me to analyse the errors and understand the SHAP graphs better.

**Sections in this notebook are**
 **[1] Imports + Dataset** : This simply loads libs needed, models that will be used - for now i just use simple logistic regression, and metrics that we will use to evaluate models

**[2] EDA Basics: **Here I do simple things like shape, describe, info etc. to get some basic idea of the dataset

**[3] EDA Features: **I look at a limited number of features and do some pre-processing on them. The  only features I do so for are: Gender, Ever_married, Smoking_status, Work_type, Residence_Type, BMI
For example for BMI which has missing values i replace them with mean. The rest are mostly changed from strings to categorical values of 0, 1 , 2

**[4] Datasets splits: **Training and Testing - create my training and testing, training is 75% . Note at this stage as I am keeping things super simple I don't bother with a validation dataset

**[5] Dataset Training: **I just train the model using logistic regression - no hyper parameter tuning with C value. Notes:
I print out the confusion matrix and evaluation metrics for training (just to see what it is)
I also print out the number of 1's and 0s predicted in training vs reality
I also print the co-efficients of the features to see which are the most important

**[6] Testing : **Basically test using predict

**[7] Error Analysis - **here I want to understand why misclassifications happened so I get the false positives and false negatives. I am getting 1 False positive and 79 false negatives. IS THAT ACTUALLY CORRECT?

 **[8] SHAP  ** - Here I run SHAP - but not sure if i'm doing it correctly

Thanks Matthew
