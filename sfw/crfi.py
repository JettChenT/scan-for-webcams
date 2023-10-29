from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2


class Clarifai:
    def __init__(self, key):
        self.channel = ClarifaiChannel.get_grpc_channel()
        self.stub = service_pb2_grpc.V2Stub(self.channel)
        self.metadata = (("authorization", f"Key {key}"),)

    def get_concepts(self, url):
        request = service_pb2.PostModelOutputsRequest(
            model_id="aaa03c23b3724a16a56b629203edc62c",
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(image=resources_pb2.Image(url=url))
                )
            ],
        )
        response = self.stub.PostModelOutputs(request, metadata=self.metadata)
        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception("Request failed, status code: " + str(response.status.code))
        return [concept.name for concept in response.outputs[0].data.concepts]
