#!/usr/bin/env python

import sys
import rospy
import math
import tf

import matplotlib as mpl
import matplotlib.cm as cm

from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point

from visualization_msgs.msg import *

from strands_navigation_msgs.msg import TopologicalNode
from topological_navigation.topological_map import *
from strands_navigation_msgs.msg import NavRoute


class edges_std_marker(object):
    
    def __init__(self, map_name) :
        self.map_name = map_name
        self.route_nodes = NavRoute()
        self.update_map(map_name)
        

    def update_map(self,map_name) :
        
        self.topo_map = topological_map(self.map_name)
        
        self.map_edges = MarkerArray()
        counter=0
        total = len(self.route_nodes.source)
        
        while counter < total :
            inds = self.topo_map._get_node_index(self.route_nodes.source[counter])
            indt = self.topo_map._get_node_index(self.route_nodes.target[counter])
            point1=Point()
            point2=Point()
            point1= (self.topo_map.nodes[inds]._get_pose()).position
            point2= (self.topo_map.nodes[indt]._get_pose()).position
            val = self.route_nodes.prob[counter]
            if not math.isnan(val) :
                self.create_edge(point1, point2, val)
            counter+=1

        idn = 0
        for m in self.map_edges.markers:
            m.id = idn
            idn += 1


    def create_edge(self, point1, point2, val):
        norm = mpl.colors.Normalize(vmin=0.0, vmax=1.0)
        cmap = cm.autumn
        m = cm.ScalarMappable(norm=norm, cmap=cmap)   

        marker = Marker()
        marker.header.frame_id = "/map"
        marker.type = marker.ARROW
        pose = Pose()
        
#        pose.position.x = (point1.x+point2.x)/2
#        pose.position.y = (point1.y+point2.y)/2
#        pose.position.z = (point1.z+point2.z)/2
        pose.position.x = point1.x
        pose.position.y = point1.y
        pose.position.z = point1.z
        angle = math.atan2((point2.y-point1.y),(point2.x-point1.x))
        
        qat = tf.transformations.quaternion_from_euler(0, 0, angle)
        pose.orientation.w = qat[3]
        pose.orientation.x = qat[0]
        pose.orientation.y = qat[1]
        pose.orientation.z = qat[2]                
        
        r = math.hypot((point2.y-point1.y),(point2.x-point1.x))/3.0
        marker.scale.x = r
        marker.scale.y = 0.1
        marker.scale.z = 0.1
                
        #val = float(counter)/float(total)
        v = m.to_rgba(1.0-val)
        marker.color.a = v[3]
        marker.color.r = v[0]
        marker.color.g = v[1]
        marker.color.b = v[2]
        marker.pose = pose
        self.map_edges.markers.append(marker)


    def received_route(self, route):
        self.route_nodes = route
        self.clear()
        self.update_map(self.topo_map)
    
    def clear(self):
        del self.map_edges