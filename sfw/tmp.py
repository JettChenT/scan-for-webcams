from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
# This is how you authenticate.
metadata = (("authorization", "Key dd2dcd9769ec4c3b8fc5061ef9e27879"),)

request = service_pb2.PostModelOutputsRequest(
    # This is the model ID of a publicly available General model. You may use any other public or custom model ID.
    model_id="aaa03c23b3724a16a56b629203edc62c",
    inputs=[
        resources_pb2.Input(
            data=resources_pb2.Data(
                image=resources_pb2.Image(
                    url="http://80.98.84.83:8080/cam_1.jpg?uniq=0.25141457991262117"
                )
            )
        )
    ],
)
response = stub.PostModelOutputs(request, metadata=metadata)

if response.status.code != status_code_pb2.SUCCESS:
    raise Exception("Request failed, status code: " + str(response.status.code))

for concept in response.outputs[0].data.concepts:
    print("%12s: %.2f" % (concept.name, concept.value))
