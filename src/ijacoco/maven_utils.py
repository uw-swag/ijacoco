import xml.etree.ElementTree as ET


# check if jacoco exists in the build plugin section, if exists, skip it
def check_jacoco_exists():
    # parse the XML file
    tree = ET.parse('pom.xml')
    root = tree.getroot()

    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
    namesp = root.tag.replace("project","") 

    # find the plugin section
    section_element = root.find(namesp+"build")
    if section_element is None:
        return False
    plugins_section = section_element.find(namesp+"plugins")
    if plugins_section is None:
        return False
    plugins = plugins_section.findall(namesp+"plugin")
    if plugins is None:
        return False
    
    for plugin in plugins:
        groupId = plugin.find(namesp+"groupId")
        # if groupId of the plugin matches org.jacoco, add a new plugin to skip jacoco
        if groupId is not None and groupId.text == "org.jacoco":
            disable_jacoco = ET.fromstring('''       
                <plugin>
                    <groupId>org.jacoco</groupId>
                    <artifactId>jacoco-maven-plugin</artifactId>
                    <configuration>
                    <skip>true</skip>
                    </configuration>
                </plugin>
            ''')
            plugins_section.append(disable_jacoco)
            tree.write('pom.xml', encoding='utf-8', xml_declaration=True)
            # print(ET.tostring(plugins_section, encoding='utf-8').decode('utf-8'))
            return True
    return False 
# updating part of the pom based by needs, called by pom_config() in build_project.py
def update_pom_config(element_name, update_content):
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse('pom.xml', parser=parser)
    root = tree.getroot()

    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")

    namesp = root.tag.replace("project","") 

    # only check for element_name == "plugin" right now, may add more by need
    if element_name == "plugin":
        section = "build"
        subsection = "plugins"
        section_element = root.find(namesp+section)
        subsection_element = section_element.find(namesp+subsection)
        update_element = ET.fromstring(f''' {update_content}''')
        subsection_element.append(update_element)

    tree.write('pom.xml', encoding='utf-8', xml_declaration=True)

    # xml_content = ET.tostring(root, encoding='utf-8').decode('utf-8')
    # print(xml_content)

def pom_add_profile(coverage_choice):
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse('pom.xml', parser=parser)
    root = tree.getroot()

    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")

    # find the <profiles> element
    namesp = root.tag.replace("project","") 
    profiles_element = root.find(namesp+'profiles')

    if profiles_element is None:
        profiles_element = ET.Element('profiles')
        root.append(profiles_element)

    retestall_profile_element = ET.fromstring('''                         
        <profile>
            <id>retestallp</id>
            <activation>
                <property>
                    <name>retestallp</name>
                </property>
            </activation>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <version>2.22.0</version>
                        <configuration>
                            <testFailureIgnore>true</testFailureIgnore>
                            <argLine>${surefireArgLine}</argLine>
                            <forkMode>once</forkMode>
                            <forkCount>1</forkCount>
                            <reuseForks>true</reuseForks>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>
    ''')

    ekstazi_profile_element = ET.fromstring(''' 
        <profile>
            <id>ekstazip</id>
            <activation>
                <property>
                    <name>ekstazip</name>
                </property>
            </activation>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.ekstazi</groupId>
                        <artifactId>ekstazi-maven-plugin</artifactId>
                        <version>5.3.0</version>
                        <executions>
                            <execution>
                                <id>ekstazi</id>
                                <goals>
                                    <goal>select</goal>
                                </goals>
                                <configuration>
                                    <xargs>dependencies.format=txt</xargs>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <version>2.22.0</version>
                        <configuration>
                            <testFailureIgnore>true</testFailureIgnore>
                            <argLine>${surefireArgLine}</argLine>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>
    ''')
    jacoco_profile_element = ET.fromstring('''                                 
        <profile>
            <id>jacocop</id>
            <activation>
                <property>
                    <name>jacocop</name>
                </property>
            </activation>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.jacoco</groupId>
                        <artifactId>jacoco-maven-plugin</artifactId>
                        <version>0.8.6</version>
                        <executions>
                            <execution>
                                <id>pre-unit-test</id>
                                <goals>
                                    <goal>prepare-agent</goal>
                                </goals>
                                <configuration>
                                    <append>false</append>
                                    <mergeOnExit>true</mergeOnExit>
                                    <dumpOnExit>true</dumpOnExit>
                                    <destFile>${project.basedir}/coverage-reports/jacoco-ut.exec</destFile>
                                    <propertyName>surefireArgLine</propertyName>
                                </configuration>
                            </execution>
                            <execution>
                                <id>post-unit-test</id>
                                <phase>test</phase>
                                <goals>
                                    <goal>report</goal>
                                </goals>
                                <configuration>
                                    <dataFile>${project.basedir}/coverage-reports/jacoco-ut.exec</dataFile>
                                    <outputDirectory>${project.basedir}/coverage-reports/jacoco-ut</outputDirectory>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <version>2.22.0</version>
                        <configuration>
                            <testFailureIgnore>true</testFailureIgnore>
                            <argLine>${surefireArgLine}</argLine>
                            <forkMode>once</forkMode>
                            <forkCount>1</forkCount>
                            <reuseForks>true</reuseForks>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>                                 
    ''')

    bjacoco_profile_element = ET.fromstring('''                                 
        <profile>
            <id>bjacocop</id>
            <activation>
                <property>
                    <name>bjacocop</name>
                </property>
            </activation>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.bjacoco</groupId>
                        <artifactId>bjacoco-maven-plugin</artifactId>
                        <version>0.8.6</version>
                        <executions>
                            <execution>
                                <id>pre-unit-test</id>
                                <goals>
                                    <goal>prepare-agent</goal>
                                </goals>
                                <configuration>
                                    <append>false</append>
                                    <mergeOnExit>true</mergeOnExit>
                                    <dumpOnExit>true</dumpOnExit>
                                    <destFile>${project.basedir}/coverage-reports/bjacoco-ut.exec</destFile>
                                    <propertyName>surefireArgLine</propertyName>
                                </configuration>
                            </execution>
                            <execution>
                                <id>post-unit-test</id>
                                <phase>test</phase>
                                <goals>
                                    <goal>report</goal>
                                </goals>
                                <configuration>
                                    <dataFile>${project.basedir}/coverage-reports/bjacoco-ut.exec</dataFile>
                                    <outputDirectory>${project.basedir}/coverage-reports/bjacoco-ut</outputDirectory>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <version>2.22.0</version>
                        <configuration>
                            <testFailureIgnore>true</testFailureIgnore>
                            <argLine>${surefireArgLine}</argLine>
                            <forkCount>1</forkCount>
                            <reuseForks>true</reuseForks>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>                                 
    ''')

    ijacoco_profile_element = ET.fromstring('''                         
        <profile>
            <id>ijacocop</id>
            <activation>
                <property>
                    <name>ijacocop</name>
                </property>
            </activation>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.ijacoco</groupId>
                        <artifactId>ijacoco-maven-plugin</artifactId>
                        <version>1.0.0</version>
                        <executions>
                            <execution>
                                <id>pre-unit-test</id>
                                <goals>
                                    <goal>prepare-agent</goal>
                                </goals>
                                <configuration>
                                    <append>false</append>
                                    <mergeOnExit>true</mergeOnExit>
                                    <dumpOnExit>true</dumpOnExit>
                                    <destFile>${project.basedir}/coverage-reports/ijacoco-ut.exec</destFile>
                                    <propertyName>surefireArgLine</propertyName>
                                </configuration>
                            </execution>
                            <execution>
                                <id>process-test-classes</id>
                                <goals>
                                    <goal>select</goal>
                                </goals>
                            </execution>
                            <execution>
                                <id>post-unit-test</id>
                                <phase>test</phase>
                                <goals>
                                    <goal>report</goal>
                                </goals>
                                <configuration>
                                    <dataFile>${project.basedir}/coverage-reports/ijacoco-ut.exec</dataFile>
                                    <outputDirectory>${project.basedir}/coverage-reports/ijacoco-ut</outputDirectory>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <version>2.22.0</version>
                        <configuration>
                            <testFailureIgnore>true</testFailureIgnore>
                            <argLine>${surefireArgLine}</argLine>
                            <forkMode>once</forkMode>
                            <forkCount>1</forkCount>
                            <reuseForks>true</reuseForks>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>
    ''')

    
    # check if the profile already exists in the pom 
    profile_exists = False
    p_list = profiles_element.findall(namesp+'profile')
    for p in p_list:
        if p.find(namesp+'id').text == coverage_choice + "p":
            profile_exists = True
            print(f"{coverage_choice}, already exists in pom.xml.")
            break

    # Add the new <profile> element to the <profiles> element
    if not profile_exists:
        if coverage_choice == "jacoco":
            profiles_element.append(jacoco_profile_element)
        elif coverage_choice == "bjacoco":
            # print(bjacoco_profile_element.type())
            profiles_element.append(bjacoco_profile_element)
        elif coverage_choice == "ijacoco":
            profiles_element.append(ijacoco_profile_element)
        elif coverage_choice == "ekstazi":
            profiles_element.append(ekstazi_profile_element)
        elif coverage_choice == "retestall":
            profiles_element.append(retestall_profile_element)

        # Save the modified XML back to the file
        tree.write('pom.xml', encoding='utf-8', xml_declaration=True)
    
    # xml_content = ET.tostring(root, encoding='utf-8').decode('utf-8')
    # print(xml_content)