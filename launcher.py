import tkinter as tk
import customtkinter
import ssl, json, socket
from pyVim import connect
from pyVmomi import vim
import webbrowser
from PIL import Image, ImageDraw
from cryptography.fernet import Fernet

def generate_key():
    f = open("encryption_key.key", "a")
    f.close()
    key = Fernet.generate_key()
    with open("encryption_key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    print(1)
    return open("encryption_key.key", "rb").read()

def encrypt_password(password, key):
    f = Fernet(key)
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password

def decrypt_password(encrypted_password, key):
    print(2)
    f = Fernet(key)
    decrypted_password = f.decrypt(encrypted_password).decode()
    return decrypted_password


def write_info(addr_entry, username_entry, password_entry):
    print(3)
    address_ip = addr_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    key = load_key()
    encrypted_password = encrypt_password(password, key)
    encrypted_password_hex = encrypted_password.hex()
    config["vcenter_host"] = address_ip
    config["vcenter_user"] = username
    config["vcenter_password"] = encrypted_password_hex

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)
    connect_login()


def connection_info():
    print(4)
    count =0
    if config["vcenter_user"]:
        count +=1
        def return_action():
            connect_login()
            destroy_connect_buttons()
        return_button = customtkinter.CTkButton(master=root,text="Back", command=return_action, width=1, height=1, fg_color=root.cget("background"), hover=None, cursor="hand2")
        return_button.pack(side="top", anchor="nw", padx=4, pady=2)

    empty_label = customtkinter.CTkLabel(root, text=" ")
    empty_label.pack(pady=5)
    
    addr_label = customtkinter.CTkLabel(root, text="IP address :")
    addr_label.pack(anchor="center")

    addr_entry = customtkinter.CTkEntry(master=root)
    addr_entry.pack(pady=5)

    username_label = customtkinter.CTkLabel(root, text="Username :")
    username_label.pack(anchor="center")

    username_entry = customtkinter.CTkEntry(master=root)
    username_entry.pack(pady=5)

    password_label = customtkinter.CTkLabel(root, text="Password :")
    password_label.pack(anchor="center")

    password_entry = customtkinter.CTkEntry(master=root, show='*')
    password_entry.pack(pady=5)

    def destroy_connect_buttons():
        empty_label.destroy()
        addr_label.destroy()
        addr_entry.destroy()
        username_label.destroy()
        username_entry.destroy()
        password_label.destroy()
        password_entry.destroy()
        submit_button.destroy()
        if count>=1:
            return_button.destroy()

    def submit_action():
        write_info(addr_entry, username_entry, password_entry)
        destroy_connect_buttons()

    submit_button = customtkinter.CTkButton(master=root, text="Submit", command=submit_action, cursor="hand2")
    submit_button.pack(pady=25)

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

    return addr_entry, username_entry, password_entry

def connect_login():
    print(5)
    vcenter_user = config["vcenter_user"]
    button = customtkinter.CTkButton(master=root, text=f"Connect as {vcenter_user}", command=connect_to_vmware, cursor="hand2")
    button.place(relx=0.5, rely=0.4, anchor="center")
    button_red = customtkinter.CTkButton(master=root, text="Other user",command=connection_info, cursor="hand2")
    button_red.place(relx=0.5, rely=0.6, anchor="center")

    def destroy_connect_buttons():
        button.destroy()
        button_red.destroy()

    button.configure(command=lambda: [destroy_connect_buttons(), connect_to_vmware()])
    button_red.configure(command=lambda: [destroy_connect_buttons(), connection_info()])

animation_index = 0
animation = ["-", "\\", "|", "/"]
canvas = None

def loading():
    print(6)
    global canvas
    canvas = tk.Canvas(root, width=100, height=100, bg=root.cget("background"), highlightthickness=0)
    canvas.pack()
    canvas.place(relx=0.5, rely=0.5, anchor="center")
    update_animation()

def update_animation():
    print(7)
    global animation_index
    if canvas:
        canvas.delete("all")
        canvas.create_text(50, 50, text=animation[animation_index], font=("Courier", 30), fill="white")
        animation_index = (animation_index + 1) % len(animation)
        canvas.after(200, update_animation)

def connect_to_vmware():
    print(8)
    vcenter_host = config["vcenter_host"]
    vcenter_user = config["vcenter_user"]

    key = load_key()
    encrypted_password_hex = config["vcenter_password"]
    encrypted_password = bytes.fromhex(encrypted_password_hex)

    vcenter_password = decrypt_password(encrypted_password, key)
    context = ssl._create_unverified_context()

    service_instance = connect.SmartConnect(
        host=vcenter_host,
        user=vcenter_user,
        pwd=vcenter_password,
        sslContext=context
    )
    content = service_instance.RetrieveContent()
    vm_access(content)
    disconnect_from_vmware(service_instance)
    return content

def disconnect_from_vmware(service_instance):
    print(9)
    connect.Disconnect(service_instance)

def screen_size():
    print(10)
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()
    margin = 30
    root.geometry(f"{x}x{y - margin}")

def open_vm_url(vm_name, id_vm, connection, guild):
    print(11)
    numMk = int(connection-1)
    char = f"{id_vm}"
    split = char.split('-')
    num = split[-1]
    vm_id = num.rstrip("'")
    vm_id = int(vm_id)
    vm_url = f"https://vcsa.chalons.univ-reims.fr/ui/webconsole.html?vmId=vm-{vm_id}&vmName={vm_name}&numMksConnections={numMk}&serverGuid={guild}&locale=en-US"
    webbrowser.open_new_tab(vm_url)

def get_clusters_hosts_pools(clusters):
    print(12)
    total_cpu_ghz = 0
    used_cpu_ghz = 0
    total_memory_gb = 0
    used_memory_gb = 0
    disp_memory = 0
    total_storage_tb = 0  
    used_storage_tb = 0  
    tt = 0
    tt_use = 0
    for cluster in clusters.view:
        hosts = cluster.host

        for host in hosts:
            total_memory_gb += host.hardware.memorySize / (1024 ** 3)
            used_memory_gb += host.summary.quickStats.overallMemoryUsage / 1024

            num_cpus = host.hardware.cpuInfo.numCpuCores
            cpu_hz = host.hardware.cpuInfo.hz
            total_cpu_ghz += (num_cpus * cpu_hz) / (10 ** 9)
            used_cpu_ghz += host.summary.quickStats.overallCpuUsage / 1000

            storage_info = host.datastore   
            for datastore in storage_info:
                summary = datastore.summary
                total_storage_tb += summary.capacity / (1024 ** 4)
                tt += total_storage_tb
                used_storage_tb += (summary.capacity - summary.freeSpace) / (1024 ** 4) 
                tt_use += used_storage_tb

    disp_memory = total_memory_gb - used_memory_gb
    disp_ghz = total_cpu_ghz - used_cpu_ghz
    disp_tt = tt - tt_use
    return total_memory_gb, used_memory_gb, disp_memory, total_cpu_ghz, used_cpu_ghz, disp_ghz, tt, tt_use, disp_tt

def vm_access(content):
    print(13)
    address_ip = config["vcenter_host"]
    vm_list = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )
    clusters = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.ClusterComputeResource], True
    )

    button_frame = customtkinter.CTkFrame(root, corner_radius=0) # Ou CTkScrollableFrame mais a besoin d'être fix
    button_frame.pack(side="left", fill="y", padx=0, ipadx=15)

    reload_arrow = Image.open('./img/refresh.png')
    reload_arrow = customtkinter.CTkImage(reload_arrow)
    def destroy_reload_button():
        button_frame.destroy()
        cluster_frame.destroy()
        info_frame.destroy()
        button.destroy()
        label_total_vm.destroy()
        label_vm_on.destroy()
        label_vm_off.destroy()
        label_cluster.destroy()
        label_memory.destroy()
        label_total_memory.destroy()
        label_free_memory.destroy()
        label_used_memory.destroy()
        label_GHz.destroy()
        label_total_GHz.destroy()
        label_used_GHz.destroy()
        label_free_GHz.destroy()
        label_total_tt.destroy()
        label_used_tt.destroy()
        label_free_tt.destroy()
        label_title.destroy()
        label_total_cluster.destroy()
        reload_button.destroy()

    reload_button = customtkinter.CTkButton(master=root, command=lambda: [destroy_reload_button(), connect_to_vmware()], cursor="hand2", image=reload_arrow, text=None, width=20, fg_color=root.cget("background"), hover_color="#333333")
    reload_arrow.configure(compound="right")
    reload_button.pack(side="top", anchor="ne", padx=5)
    
    title_frame = customtkinter.CTkFrame(root, fg_color=root.cget("background"), corner_radius=0)
    title_frame.pack(side="top", anchor="n", padx=10, pady=0)

    try:
        name, _, _ = socket.gethostbyaddr(address_ip)
    except:
        name = address_ip

    memory_stockage_GHz_frame = customtkinter.CTkFrame(root, fg_color=root.cget("background"), corner_radius=0)
    memory_stockage_GHz_frame.pack(side="bottom", anchor="s", padx=50, pady=0, fill="both")

    memory_frame = customtkinter.CTkFrame(memory_stockage_GHz_frame, fg_color=root.cget("background"), corner_radius=0)
    memory_frame.pack(side="left", anchor="sw", padx=50, pady=50, fill="both")

    tt_frame = customtkinter.CTkFrame(memory_stockage_GHz_frame, fg_color=root.cget("background"), corner_radius=0)
    tt_frame.pack(side="right", anchor="se", padx=50, pady=50, fill="both")

    GHz_frame = customtkinter.CTkFrame(root, fg_color=root.cget("background"), corner_radius=0)
    GHz_frame.pack(side="bottom", anchor="n", padx=100, pady=80)

    info_frame = customtkinter.CTkFrame(root, fg_color=root.cget("background"), corner_radius=0)
    info_frame.pack(side="left", anchor="nw", padx=100, pady=50)

    cluster_frame = customtkinter.CTkFrame(root, fg_color=root.cget("background"), corner_radius=0)
    cluster_frame.pack(side="right", anchor="ne", padx=100, pady=50) 

    guild_content = content.about.instanceUuid

    vm_on_count = 0
    vm_off_count = 0
    total_vm_count = 0

    for vm in vm_list.view:
        image_size = (30, 30)
        circle_size = (10, 10)

        image = Image.new("RGBA", image_size)
        draw = ImageDraw.Draw(image)

        if vm.runtime.powerState == "poweredOn":
            vm_on_count += 1
            draw.ellipse((0, 0, circle_size[0], circle_size[1]), fill="green")
        else:
            vm_off_count += 1
            draw.ellipse((0, 0, circle_size[0], circle_size[1]), fill="red")

        total_vm_count += 1

        dot = customtkinter.CTkImage(image)

        button_text = f"{vm.name}{' ' * 2}" 

        button = customtkinter.CTkButton(
            button_frame,
            text=button_text,
            command=lambda name=vm.name, id_vm=vm.environmentBrowser, connection=vm.runtime.numMksConnections, guild=guild_content: open_vm_url(name, id_vm, connection, guild),
            fg_color="#333333",
            width=15,
            height=1,
            anchor='w',
            hover_color="#404040",
            cursor="hand2"
        )

        button.configure(image=dot, compound="left")
        button.pack(side="top", anchor="nw", pady=0, fill='both', padx=0)
        button_frame.configure(fg_color="#333333")

    host_count = 0
    host_on_count = 0
    host_off_count = 0
    for cluster in clusters.view:
        hosts = cluster.host
        for host in hosts:
            if host.runtime.powerState == "poweredOn":
                host_on_count += 1
            elif host.runtime.powerState == "poweredOff":
                host_off_count += 1

            host_count += 1
            #host_name = host.name

    label_title = customtkinter.CTkLabel(title_frame, text=name, font=("Helvetica", 24, "bold"), fg_color=root.cget("background"), anchor="center")
    label_title.grid(row=0, column=1, sticky="w", padx=10, pady=10)

    label_vms = customtkinter.CTkLabel(info_frame, text="  VMs  ", font=("Helvetica", 24, "bold"), fg_color=root.cget("background"), anchor="center")
    label_vms.grid(row=0, column=1, sticky="w", padx=10, pady=10)

    label_vm_on = customtkinter.CTkLabel(info_frame, text=f"VMs On: {vm_on_count}", fg_color=root.cget("background"), anchor="center")
    label_vm_on.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    label_vm_off = customtkinter.CTkLabel(info_frame, text=f"VMs Off: {vm_off_count}", fg_color=root.cget("background"), anchor="center")
    label_vm_off.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    label_total_vm = customtkinter.CTkLabel(info_frame, text=f"Total VMs: {total_vm_count}", fg_color=root.cget("background"), anchor="center")
    label_total_vm.grid(row=1, column=2, sticky="w", padx=10, pady=5)

    label_cluster = customtkinter.CTkLabel(cluster_frame, text="Hosts", font=("Helvetica", 24, "bold"), fg_color=root.cget("background"), anchor="center")
    label_cluster.grid(row=0, column=1, sticky="w", padx=10, pady=10)

    label_total_cluster = customtkinter.CTkLabel(cluster_frame, text=f"Hosts On: {host_on_count}", fg_color=root.cget("background"), anchor="center")
    label_total_cluster.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    label_total_cluster = customtkinter.CTkLabel(cluster_frame, text=f"Hosts Off: {host_off_count}", fg_color=root.cget("background"), anchor="center")
    label_total_cluster.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    label_total_cluster = customtkinter.CTkLabel(cluster_frame, text=f"Total Hosts: {host_count}", fg_color=root.cget("background"), anchor="center")
    label_total_cluster.grid(row=1, column=2, sticky="w", padx=10, pady=5)

    ###############################

    total_info = get_clusters_hosts_pools(clusters)
    label_memory = customtkinter.CTkLabel(memory_frame, text="Memory", font=("Helvetica", 24, "bold"), fg_color=root.cget("background"), anchor="center")
    label_memory.grid(row=0, column=1, sticky="w", padx=10, pady=10)

    label_used_memory = customtkinter.CTkLabel(memory_frame, text=f"{total_info[1]:.2f} GB used", fg_color=root.cget("background"), anchor="center")
    label_used_memory.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    label_total_memory = customtkinter.CTkLabel(memory_frame, text=f"{total_info[0]:.2f} GB total", fg_color=root.cget("background"), anchor="center")
    label_total_memory.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    label_free_memory = customtkinter.CTkLabel(memory_frame, text=f"{total_info[2]:.2f} GB free", fg_color=root.cget("background"), anchor="center")
    label_free_memory.grid(row=1, column=2, sticky="w", padx=10, pady=5)

    ###############################

    label_GHz = customtkinter.CTkLabel(GHz_frame, text="GHz", font=("Helvetica", 24, "bold"), fg_color=root.cget("background"), anchor="center")
    label_GHz.grid(row=0, column=1, sticky="w", padx=10, pady=10)

    label_used_GHz= customtkinter.CTkLabel(GHz_frame, text=f"{total_info[4]:.2f} GHz used", fg_color=root.cget("background"), anchor="center")
    label_used_GHz.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    label_total_GHz = customtkinter.CTkLabel(GHz_frame, text=f"{total_info[3]:.2f} GHz total", fg_color=root.cget("background"), anchor="center")
    label_total_GHz.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    label_free_GHz = customtkinter.CTkLabel(GHz_frame, text=f"{total_info[5]:.2f} GHz free", fg_color=root.cget("background"), anchor="center")
    label_free_GHz.grid(row=1, column=2, sticky="w", padx=10, pady=5)

    ###############################

    label_tt = customtkinter.CTkLabel(tt_frame, text="Stockage", font=("Helvetica", 24, "bold"), fg_color=root.cget("background"), anchor="center")
    label_tt.grid(row=0, column=1, sticky="w", padx=10, pady=10)

    label_used_tt= customtkinter.CTkLabel(tt_frame, text=f"{total_info[7]:.2f} TB used", fg_color=root.cget("background"), anchor="center")
    label_used_tt.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    label_total_tt = customtkinter.CTkLabel(tt_frame, text=f"{total_info[6]:.2f} TB total", fg_color=root.cget("background"), anchor="center")
    label_total_tt.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    label_free_tt = customtkinter.CTkLabel(tt_frame, text=f"{total_info[8]:.2f} TB free", fg_color=root.cget("background"), anchor="center")
    label_free_tt.grid(row=1, column=2, sticky="w", padx=10, pady=5)

    screen_size()
    

if __name__ == "__main__":
    try:
        customtkinter.set_appearance_mode("dark")
        root = customtkinter.CTk()
        root.geometry("300x400")
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            if config["vcenter_user"]:
                connect_login()
            else:
                connection_info()
    except FileNotFoundError:
        config = {
        "vcenter_host": "",
        "vcenter_user": "",
        "vcenter_password": ""
        }
        generate_key()
        connection_info()

    root.title("VmWare GUI")
    root.mainloop()
