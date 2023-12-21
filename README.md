# GNMI Server Simulator

## Description:

GNMI Server Simulator is a simple tool desinged to emulate GNMI enabled devices,providing testing environment for GNMI clients.

## How to use
1) Download the container image  
```
docker pull nareshkumar237n/gnmi_simulator
```
2) Create a directory to add yang paths for the simulator
   ### Example
   ```
   mkdir /tmp/yang_paths/
   ```
   **Note** : It can be any directory
   
3) Create **paths.txt** file under **/tmp/yang_paths** and add path for which you want to send subscribe response to client
   ### Example
   ```
   If you want to subscribe to paths /a/b[name=*]/c which provides string as response,
   than add below text in paths.txt file
   
   /a/b/[name=test]/c="output"

   In case if response is integer than add text as mentioned below

   /a/b/[name=test]/c=10
   
   Note: test,output,10 are sample text, it can be changed as per your need.
   ```
4) Create **get_paths.txt** file under **/tmp/yang_paths** and add paths for which you want to send get response to client
   
5) Run the container
```
docker run -d -p 50051:50051 -v /tmp/yang_paths/:/app/paths/ <image_id>
```
