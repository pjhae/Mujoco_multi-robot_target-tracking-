import numpy as np
import matplotlib.pyplot as plt
from gym import utils
from gym.envs.mujoco import mujoco_env


# if you want to receive pixel data from camera using render("rgb_array",_,_,_,_)
# you should change below line <site_packages>/gym/envs/mujoco/mujoco_env.py to:
# self.viewer = mujoco_py.MjRenderContextOffscreen(self.sim, None, -1)


DEFAULT_CAMERA_CONFIG = {
    'distance': 1.5,
}


class HexyEnv(mujoco_env.MujocoEnv, utils.EzPickle):
    def __init__(self, xml_file='Hexy_ver_2.3/hexy-v2.3.xml', ):
        utils.EzPickle.__init__(**locals())
        self.time_step = 0

        self.interval = 5

        #### For Following Agent
        self.xlist_1 = []
        self.ylist_1 = []

        #### For Reference Agent
        self.xlist_2 = []
        self.ylist_2 = []

        ## For vel check
        self.vel = []

        ## Distance between 2 agents
        self.dist_between_agents = 0

        mujoco_env.MujocoEnv.__init__(self, xml_file, 5)


    @property
    def is_healthy(self):
        # if height of hexy is too low or distance between two agent is too far, reset!!

        is_healthy = (self.state_vector()[2]) > -0.05 and self.dist_between_agents < 0.75

        traget_body_array   = ["T_BRf1", "T_BRf2", "T_BRf3", "T_BRf4", "T_BLf1", "T_BLf2", "T_BLf3", "T_BLf4", "T_BLt1", "T_BLt2", "T_BLs1", "Torso_2"]
        follower_body_array = ["F_FRf1", "F_FRf2", "F_FRf3", "F_FRf4", "F_FLf1", "F_FLf2", "F_FLf3", "F_FLf4", "F_FLt1", "F_FLt2", "F_FLs1", "Torso"]

        for i in range(self.sim.data.ncon):
             sim_contact = self.sim.data.contact[i]
             for j in range(len(traget_body_array)):
                 if (str(self.sim.model.geom_id2name(sim_contact.geom1)) == traget_body_array[j]):
                    if str(self.sim.model.geom_id2name(sim_contact.geom2)) in follower_body_array :
                        is_healthy = False
                        print("Collision! : RESET")
                        return is_healthy

                 if (str(self.sim.model.geom_id2name(sim_contact.geom2)) == traget_body_array[j]):
                     if str(self.sim.model.geom_id2name(sim_contact.geom1)) in follower_body_array:
                         is_healthy = False
                         print("Collision! : RESET")
                         return is_healthy

        return is_healthy


    @property
    def done(self):
        done = not self.is_healthy
        return done


    def step(self, action):
        # print(action.shape)
        action = action[0:18]

        # Turn Right
        Act1 = np.array([0.0, -0.75, 0.4,
                         -0.3, -0.75, 0.4,
                         0.3, -0.75, 0.8,
                         0.6, -0.75, 0.8,
                         -0.6, -0.75, 0.4,
                         0.0, -0.75, 0.4])

        Act3 = np.array([-0.3, -0.75, 0.8,
                         0.3, -0.75, 0.4,
                         0.0, -0.75, 0.4,
                         0.0, -0.75, 0.4,
                         0.6, -0.75, 0.4,
                         -0.6, -0.75, 0.8])

        Act2 = (Act1 + Act3) / 2
        Act2[4] += 0.75
        Act2[10] += 0.75
        Act2[16] += 0.75

        Act4 = (Act1 + Act3) / 2
        Act4[1] += 0.5
        Act4[7] += 0.5
        Act4[13] += 0.5

        Turn_Right = [Act1, Act2, Act3, Act4]


        # Turn Left

        Act1 = np.array([0.0, -0.75, 0.4,
                         -0.6, -0.75, 0.4,
                         0.6, -0.75, 0.8,
                         0.3, -0.75, 0.8,
                         -0.3, -0.75, 0.4,
                         0.0, -0.75, 0.4])

        Act3 = np.array([-0.6, -0.75, 0.8,
                         0.6, -0.75, 0.4,
                         0.0, -0.75, 0.4,
                         0.0, -0.75, 0.4,
                         0.3, -0.75, 0.4,
                         -0.3, -0.75, 0.8])

        Act2 = (Act1 + Act3) / 2
        Act2[4] += 0.5
        Act2[10] += 0.5
        Act2[16] += 0.5

        Act4 = (Act1 + Act3) / 2
        Act4[1] += 0.75
        Act4[7] += 0.75
        Act4[13] += 0.75

        Turn_Left = [Act1, Act2, Act3, Act4]


        # Go-straight
        Act1 = np.array([0.0, -0.75, 0.4,
                         -0.6, -0.75, 0.4,
                         0.6, -0.75, 0.8,
                         0.6, -0.75, 0.8,
                         -0.6, -0.75, 0.4,
                         0.0, -0.75, 0.4])

        Act3 = np.array([-0.6, -0.75, 0.8,
                         0.6, -0.75, 0.4,
                         0.0, -0.75, 0.4,
                         0.0, -0.75, 0.4,
                         0.6, -0.75, 0.4,
                         -0.6, -0.75, 0.8])

        Act2 = (Act1 + Act3) / 2
        Act2[4] += 0.5
        Act2[10] += 0.5
        Act2[16] += 0.5

        Act4 = (Act1 + Act3) / 2
        Act4[1] += 0.5
        Act4[7] += 0.5
        Act4[13] += 0.5

        Go_straight = [Act1, Act2, Act3, Act4]


        #### Designing Action Sequence
        Action_dct = {}
        Action_dct["Go_straight"] = Go_straight
        Action_dct["Turn_Right"] = Turn_Right
        Action_dct["Turn_Left"] = Turn_Left

        Action_sequence = ["Go_straight"] *10 + ["Turn_Left"]*10 +["Go_straight"] *10  +["Turn_Right"] * 20 +["Go_straight"] *10 + ["Turn_Left"]*20 +["Go_straight"] *10+ ["Turn_Right"] * 20 +["Go_straight"] *10 + ["Turn_Left"]*20 +["Go_straight"] *20
        ## How to calculate time-step ?  =>  (160) * 4 * Interval(5) = 3200

        motion = Action_dct[Action_sequence [  (self.time_step // (4*self.interval)) ]  ]  [(self.time_step%(4*self.interval))//(self.interval)]
        # motion = [0]*18

        # self.set_state(np.hstack((self.sim.get_state().qpos[0:30] ,motion))  , np.hstack((self.sim.get_state().qvel[0:30],[0.4]*18)))


        #### Get initial INFO
        x_1_init = self.state_vector()[0]
        y_1_init = self.state_vector()[1]

        x_2_init = self.state_vector()[24]+0.45
        y_2_init = self.state_vector()[25]


        #### Do Simulation
        self.do_simulation(np.hstack((action,motion)), self.frame_skip)


        #### Calculate rewards and costs

        ## Position
        x_1_pos = self.state_vector()[0]
        y_1_pos = self.state_vector()[1]
        x_2_pos = self.state_vector()[24]+0.45
        y_2_pos = self.state_vector()[25]

        ## Velocity
        x_1_vel = (x_1_pos - x_1_init) / self.dt
        y_1_vel = (y_1_pos - y_1_init) / self.dt
        x_2_vel = (x_2_pos - x_2_init) / self.dt
        y_2_vel = (y_2_pos - y_2_init) / self.dt

        ## Planar velocity
        xy_1_vel = np.sqrt(np.mean(np.square(np.array([x_1_vel, y_1_vel]))))
        xy_2_vel = np.sqrt(np.mean(np.square(np.array([x_2_vel, y_2_vel]))))

        ## Check coordinate
        # print("Following :", x_1_pos, y_1_pos)
        # print("Ref :", x_2_pos, y_2_pos )

        ## Distance between two agents (initially d=0.5)
        Distance_between_two_agents = ((x_1_pos-x_2_pos)**2 + (y_1_pos - y_2_pos)**2)**(0.5)
        self.dist_between_agents = Distance_between_two_agents

        #### Rewards (사이의 거리, 속도, 충돌)
        # Distance reward
        dist_reward = np.exp(-100 * (0.45 - Distance_between_two_agents ) ** 2)

        # Velocity reward
        vel_reward = 5* np.exp(-3000*(0.05-xy_1_vel)**2)

        # Collision reward
        col_reward = 0
        traget_body_array   = ["T_BRf1", "T_BRf2", "T_BRf3", "T_BRf4", "T_BLf1", "T_BLf2", "T_BLf3", "T_BLf4", "T_BLt1", "T_BLt2", "T_BLs1", "Torso_2"]
        follower_body_array = ["F_FRf1", "F_FRf2", "F_FRf3", "F_FRf4", "F_FLf1", "F_FLf2", "F_FLf3", "F_FLf4", "F_FLt1", "F_FLt2", "F_FLs1", "Torso"]

        for i in range(self.sim.data.ncon):
             sim_contact = self.sim.data.contact[i]
             for j in range(len(traget_body_array)):
                 if (str(self.sim.model.geom_id2name(sim_contact.geom1)) == traget_body_array[j]):
                    if str(self.sim.model.geom_id2name(sim_contact.geom2)) in follower_body_array :
                        col_reward = -50
                        print("Collision! : Reward -= 50")
                        break

                 if (str(self.sim.model.geom_id2name(sim_contact.geom2)) == traget_body_array[j]):
                     if str(self.sim.model.geom_id2name(sim_contact.geom1)) in follower_body_array:
                        col_reward = -50
                        print("Collision! : Reward -= 50")
                        break
        # Survival reward
        ser_reward = 0.1

        # Reward sum
        reward = dist_reward + vel_reward + col_reward +  ser_reward

        # print("dist : " ,dist_reward, "vel :", vel_reward,"ser :", ser_reward, "sum : ", reward)


        #### Append postion of Two agents
        # For reference agent
        self.xlist_2.append(x_2_pos)
        self.ylist_2.append(y_2_pos)

        # For following agent
        self.xlist_1.append(x_1_pos)
        self.ylist_1.append(y_1_pos)

        # ## Plotting Trajectory
        # if self.time_step == 30 - 1 :     # max_episode_steps - 1
        #     plt.plot(self.xlist_2[2:], self.ylist_2[2:], 'r-', label='reference_agent')
        #     plt.plot(self.xlist_1[2:], self.ylist_1[2:], 'b-', label='following_agent')
        #     #plt.plot(self.vel)
        #     plt.legend()
        #     plt.show()

        #### Update time step
        self.time_step += 1

        #### Return INFOs
        done = self.done
        observation = self._get_obs()
        info = {

            'total reward': reward
        }

        return observation, reward, done, info


    def _get_obs(self):

        ## 1. For Training
        camera_data = np.array(self.render("rgb_array", 148, 148, 2))
        CHW = np.transpose(camera_data, (2, 0, 1))

        ## If you wanna check the input image
        #plt.imshow(camera_data)
        #plt.show()

        ## 2. For rendering check
        #data = self._get_viewer("rgb_array").read_pixels(148, 148, depth=False)
        #CHW = np.transpose(data[::-1, :, :] , (2, 0, 1))

        obs_dct = {}
        obs_dct['image'] = np.array(CHW)/255.0
        obs_dct['vector'] = self.state_vector()[6:24]
        return obs_dct


    def reset_model(self):

        ## Reset all Joint to zero position
        qpos = np.array(
            [0, 0.0, -0.005, 0, 0, 0, 0, -0.8, 0.6, 0, -0.8, 0.6, 0, -0.8, 0.6, 0, -0.8, 0.6, 0, -0.8, 0.6, 0, -0.8,0.6,
             0, 0.0, -0.005, 0, 0, 0, 0, -0.8, 0.6, 0, -0.8, 0.6, 0, -0.8, 0.6, 0, -0.8, 0.6, 0, -0.8, 0.6, 0, -0.8, 0.6])
        qvel = np.array([0]*48)
        self.set_state(qpos, qvel)

        ## Update obervation
        observation = self._get_obs()

        ## Initialize timestep
        self.time_step = 0

        # Clear the batch
        self.xlist_1 = []
        self.ylist_1 = []
        self.xlist_2 = []
        self.ylist_2 = []
        self.vel = []

        return observation

    def viewer_setup(self):
        for key, value in DEFAULT_CAMERA_CONFIG.items():
            if isinstance(value, np.ndarray):
                getattr(self.viewer.cam, key)[:] = value
            else:
                setattr(self.viewer.cam, key, value)


