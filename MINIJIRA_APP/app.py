#!/usr/bin/env python3

import aws_cdk as cdk

from minijira_app.minijira_app_stack import MinijiraAppStack


app = cdk.App()
MinijiraAppStack(app, "minijira-app")

app.synth()
