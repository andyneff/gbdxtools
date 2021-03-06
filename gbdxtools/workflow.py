"""
Authors: Kostas Stamatiou, Donnie Marino, Dan Getman, Dahl Winters, Nate Ricklin


GBDX Workflow interface.

"""
from __future__ import print_function
from builtins import object

import json


class Workflow(object):
    def __init__(self, interface):
        """Construct the Workflow instance
        
        Args:
            interface (Interface): A reference to the GBDX Interface.

        Returns:
            An instance of the Workflow class.
        """
        # store a reference to the GBDX Connection
        self.gbdx_connection = interface.gbdx_connection

        # store a ref to the s3 interface
        self.s3 = interface.s3

        # the logger
        self.logger = interface.logger

    def launch(self, workflow):
        """Launches GBDX workflow.

        Args:
            workflow (dict): Dictionary specifying workflow tasks.

        Returns:
            Workflow id (str).
        """

        # hit workflow api
        url = 'https://geobigdata.io/workflows/v1/workflows'
        try:
            r = self.gbdx_connection.post(url, json=workflow)
            try:
                r.raise_for_status()
            except:
                print("GBDX API Status Code: %s" % r.status_code)
                print("GBDX API Response: %s" % r.text)
                r.raise_for_status()
            workflow_id = r.json()['id']
            return workflow_id
        except TypeError:
            self.logger.debug('Workflow not launched!')

    def status(self, workflow_id):
        """Checks workflow status.

         Args:
             workflow_id (str): Workflow id.

         Returns:
             Workflow status (str).
        """
        self.logger.debug('Get status of workflow: ' + workflow_id)
        url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id
        r = self.gbdx_connection.get(url)

        return r.json()['state']

    def events(self, workflow_id):
        '''Get workflow events.

         Args:
             workflow_id (str): Workflow id.

         Returns:
             List of workflow events.
        '''
        self.logger.debug('Get events of workflow: ' + workflow_id)
        url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id + '/events'
        r = self.gbdx_connection.get(url)

        return r.json()['Events']

    def cancel(self, workflow_id):
        """Cancels a running workflow.

           Args:
               workflow_id (str): Workflow id.

           Returns:
               Nothing
        """
        self.logger.debug('Canceling workflow: ' + workflow_id)
        url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id + '/cancel'
        r = self.gbdx_connection.post(url, data='')
        r.raise_for_status()

    def list_tasks(self):
        """Get a list of all the workflow task definitions I'm allowed to see
            
            Args:
                None
    
            Returns:
                Task list (list)

        """
        url = 'https://geobigdata.io/workflows/v1/tasks'
        r = self.gbdx_connection.get(url)
        r.raise_for_status()
        return r.json()

    def describe_task(self, task_name):
        """Get the task definition.

         Args:
             task_name (str): The task name.

         Return:
             Task definition (dict).
        """

        url = 'https://geobigdata.io/workflows/v1/tasks/' + task_name
        r = self.gbdx_connection.get(url)
        r.raise_for_status()

        return r.json()

    def launch_batch_workflow(self, batch_workflow):
        """Launches GBDX batch workflow.

        Args:
            batch_workflow (dict): Dictionary specifying batch workflow tasks.

        Returns:
            Batch Workflow id (str).
        """

        # hit workflow api
        url = 'https://geobigdata.io/workflows/v1/batch_workflows'
        try:
            r = self.gbdx_connection.post(url, json=batch_workflow)
            batch_workflow_id = r.json()['batch_workflow_id']
            return batch_workflow_id
        except TypeError as e:
            self.logger.debug('Batch Workflow not launched, reason: {0}'.format(e.message))

    def batch_workflow_status(self, batch_workflow_id):
        """Checks GBDX batch workflow status.

         Args:
             batch workflow_id (str): Batch workflow id.

         Returns:
             Batch Workflow status (str).
        """
        self.logger.debug('Get status of batch workflow: ' + batch_workflow_id)
        url = 'https://geobigdata.io/workflows/v1/batch_workflows/' + batch_workflow_id
        r = self.gbdx_connection.get(url)

        return r.json()

    def batch_workflow_cancel(self, batch_workflow_id):
        """Cancels GBDX batch workflow.

         Args:
             batch workflow_id (str): Batch workflow id.

         Returns:
             Batch Workflow status (str).
        """
        self.logger.debug('Cancel batch workflow: ' + batch_workflow_id)
        url = 'https://geobigdata.io/workflows/v1/batch_workflows/{0}/cancel'.format(batch_workflow_id)
        r = self.gbdx_connection.post(url)

        return r.json()

    def launch_aop_to_s3(self,
                         input_location,
                         output_location,
                         bands='Auto',
                         ortho_epsg='EPSG:4326',
                         enable_pansharpen='false',
                         enable_acomp='false',
                         enable_dra='false',
                         ):

        """Launch aop_to_s3 workflow with choice of select parameters. There
           are more parameter choices to this workflow than the ones provided
           by this function. In this case, use the more general
           launch_workflow function.

           Args:
               input_location (str): Imagery location on S3.
               output_location (str): Output imagery S3 location within user prefix.
                                      This should not be preceded with nor followed
                                      by a backslash.
               bands (str): Bands to process (choices are 'Auto', 'MS', 'PAN', default
                            is 'Auto'). If enable_pansharpen = 'true', leave the default
                            setting.
               ortho_epsg (str): Choose projection (default 'EPSG:4326').
               enable_pansharpen (str): Apply pansharpening (default 'false').
               enable_acomp (str): Apply ACOMP (default 'false').
               enable_dra (str): Apply dynamic range adjust (default 'false').
           Returns:
               Workflow id (str).
        """

        # create workflow dictionary
        aop_to_s3 = json.loads("""{
        "tasks": [{
        "containerDescriptors": [{
            "properties": {"domain": "raid"}}],
        "name": "AOP",
        "inputs": [{
            "name": "data",
            "value": "INPUT_BUCKET"
        }, {
            "name": "bands",
            "value": "Auto"
        },
           {
            "name": "enable_acomp",
            "value": "false"
        }, {
            "name": "enable_dra",
            "value": "false"
        }, {
            "name": "ortho_epsg",
            "value": "EPSG:4326"
        }, {
            "name": "enable_pansharpen",
            "value": "false"
        }],
        "outputs": [{
            "name": "data"
        }, {
            "name": "log"
        }],
        "timeout": 36000,
        "taskType": "AOP_Strip_Processor",
        "containerDescriptors": [{"properties": {"domain": "raid"}}]
        }, {
        "inputs": [{
            "source": "AOP:data",
            "name": "data"
        }, {
            "name": "destination",
            "value": "OUTPUT_BUCKET"
        }],
        "name": "StageToS3",
        "taskType": "StageDataToS3",
        "containerDescriptors": [{"properties": {"domain": "raid"}}]
        }],
        "name": "aop_to_s3"
        }""")

        aop_to_s3['tasks'][0]['inputs'][0]['value'] = input_location
        aop_to_s3['tasks'][0]['inputs'][1]['value'] = bands
        aop_to_s3['tasks'][0]['inputs'][2]['value'] = enable_acomp
        aop_to_s3['tasks'][0]['inputs'][3]['value'] = enable_dra
        aop_to_s3['tasks'][0]['inputs'][4]['value'] = ortho_epsg
        aop_to_s3['tasks'][0]['inputs'][5]['value'] = enable_pansharpen

        # use the user bucket and prefix information to set output location
        bucket = self.s3.info['bucket']
        prefix = self.s3.info['prefix']
        output_location_final = 's3://' + '/'.join([bucket, prefix, output_location])
        aop_to_s3['tasks'][1]['inputs'][1]['value'] = output_location_final

        # launch workflow
        self.logger.debug('Launch workflow')
        workflow_id = self.launch(aop_to_s3)

        return workflow_id
