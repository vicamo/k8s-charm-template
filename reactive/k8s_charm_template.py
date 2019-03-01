from charmhelpers.core import hookenv
from charms.reactive import set_flag, clear_flag
from charms.reactive import when_all, when_any, when_not

from charms import layer


@when_all('layer.docker-resource.my-image.available',
          'layer.docker-resource.my-other-image.available')
@when_not('charm.k8s-charm-template.started')
def start_charm():
    layer.status.maintenance('starting workload')

    # fetch the info (registry path, auth info) about the images
    image1_info = layer.docker_resource.get_info('my-image')
    image2_info = layer.docker_resource.get_info('my-other-image')

    # this can also be handed raw YAML, so some charm authors
    # choose to use templated YAML in a file instead
    layer.caas_base.pod_spec_set({
        'containers': [
            {
                'name': 'k8s-charm-template-service1',
                'imageDetails': {
                    'imagePath': image1_info.registry_path,
                    'username': image1_info.username,
                    'password': image1_info.password,
                },
                'command': [],
                'args': [ "--arg1", "--arg2"],
                'ports': [
                    {
                        'name': 'website1',
                        'containerPort': 80,
                    },
                ],
                'config': {
                    'MY_ENV_VAR': hookenv.model_name(),
                },
            },
            {
                'name': 'k8s-charm-template-service2',
                'imageDetails': {
                    'imagePath': image2_info.registry_path,
                    'username': image2_info.username,
                    'password': image2_info.password,
                },
                'command': [],
                'ports': [
                    {
                        'name': 'website2',
                        'containerPort': 8080,
                    },
                ],
                'config': {
                    'MY_ENV_VAR': hookenv.model_name(),
                },
            },
        ],
    })

    layer.status.active('ready')
    set_flag('charm.k8s-charm-template.started')


@when_any('layer.docker-resource.my-image.changed',
          'layer.docker-resource.my-other-image.changed')
def update_image():
    # handle a new image resource becoming available
    clear_flag('charm.k8s-charm-template.started')
